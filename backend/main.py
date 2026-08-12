from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import Response, StreamingResponse
import pandas as pd
from io import StringIO
import json
import io
import csv
import bcrypt

from backend.rules import (
    check_missing_values,
    check_duplicates,
    check_multiple_ranges,
    check_frozen_values,
)
from backend.database import SessionLocal, AnalysisRun, User
from backend.report import generate_pdf_report

app = FastAPI()


def run_analysis(df, range_configs, ignore_columns):
    missing = check_missing_values(df)

    ignore_list = ignore_columns.split(",") if ignore_columns else []
    duplicates = check_duplicates(df, ignore_columns=ignore_list)

    outliers_by_column = check_multiple_ranges(df, range_configs) if range_configs else {}

    frozen_columns = check_frozen_values(df, ignore_columns=ignore_list)

    all_outlier_indices = set()
    for outlier_df in outliers_by_column.values():
        all_outlier_indices |= set(outlier_df.index)

    anomalous_indices = set(missing.index) | set(duplicates.index) | all_outlier_indices
    clean_rows = len(df) - len(anomalous_indices)
    quality_score = round(100 * clean_rows / len(df), 1) if len(df) > 0 else 0

    return missing, outliers_by_column, duplicates, quality_score, frozen_columns


def build_result(df, range_configs, ignore_columns):
    missing, outliers_by_column, duplicates, quality_score, frozen_columns = run_analysis(
        df, range_configs, ignore_columns
    )

    outliers_response = {
        col: df_out.astype(object).where(pd.notnull(df_out), None).to_dict(orient="records")
        for col, df_out in outliers_by_column.items()
    }

    return {
        "missing": missing.astype(object).where(pd.notnull(missing), None).to_dict(orient="records"),
        "outliers_by_column": outliers_response,
        "duplicates": duplicates.astype(object).where(pd.notnull(duplicates), None).to_dict(orient="records"),
        "quality_score": quality_score,
        "total_rows": len(df),
        "missing_count": len(missing),
        "duplicate_count": len(duplicates),
        "outlier_count": sum(len(v) for v in outliers_response.values()),
        "frozen_columns": frozen_columns,
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile,
    range_configs: str = Form(None),
    ignore_columns: str = Form(None),
):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    configs = json.loads(range_configs) if range_configs else []
    result = build_result(df, configs, ignore_columns)

    session = SessionLocal()
    run = AnalysisRun(
        filename=file.filename,
        total_rows=result["total_rows"],
        missing_count=result["missing_count"],
        outlier_count=result["outlier_count"],
        duplicate_count=result["duplicate_count"],
        quality_score=result["quality_score"],
    )
    session.add(run)
    session.commit()
    session.close()

    return result


@app.get("/history")
def get_history():
    session = SessionLocal()
    runs = session.query(AnalysisRun).all()
    session.close()

    return [
        {
            "filename": r.filename,
            "timestamp": str(r.timestamp),
            "total_rows": r.total_rows,
            "missing": r.missing_count,
            "outliers": r.outlier_count,
            "duplicates": r.duplicate_count,
            "quality_score": r.quality_score,
        }
        for r in runs
    ]


@app.post("/generate-report")
async def generate_report(
    file: UploadFile,
    range_configs: str = Form(None),
    ignore_columns: str = Form(None),
):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    configs = json.loads(range_configs) if range_configs else []
    result = build_result(df, configs, ignore_columns)

    pdf_bytes = generate_pdf_report(file.filename, result)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=rapport_{file.filename}.pdf"},
    )


@app.post("/export-csv")
async def export_csv(
    file: UploadFile,
    range_configs: str = Form(None),
    ignore_columns: str = Form(None),
):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    configs = json.loads(range_configs) if range_configs else []
    result = build_result(df, configs, ignore_columns)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Type d'anomalie", "Colonne", "Détail"])

    for row in result["missing"]:
        writer.writerow(["Valeur manquante", "", row])

    for column, rows in result["outliers_by_column"].items():
        for row in rows:
            writer.writerow(["Hors seuil", column, row])

    for row in result["duplicates"]:
        writer.writerow(["Doublon", "", row])

    for row in result["frozen_columns"]:
        writer.writerow(["Valeur figée", row["column"], f"{row['valeur_figee']} ({row['nombre_lignes']} lignes)"])

    output.seek(0)
    csv_bytes = output.getvalue().encode("utf-8-sig")

    return StreamingResponse(
        io.BytesIO(csv_bytes),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=anomalies_{file.filename}.csv"},
    )

@app.post("/register")
def register(
    username: str = Form(...),
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
):
    session = SessionLocal()

    existing = session.query(User).filter(User.username == username).first()
    if existing:
        session.close()
        return {"status": "error", "message": "Ce nom d'utilisateur existe deja."}

    existing_email = session.query(User).filter(User.email == email).first()
    if existing_email:
        session.close()
        return {"status": "error", "message": "Cet email est deja utilise."}

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = User(username=username, full_name=full_name, email=email, password_hash=password_hash)
    session.add(new_user)
    session.commit()
    session.close()

    return {"status": "ok", "message": "Compte cree avec succes."}


@app.post("/login")
def login(username: str = Form(...), password: str = Form(...)):
    session = SessionLocal()
    user = session.query(User).filter(User.username == username).first()
    session.close()

    if not user:
        return {"status": "error", "message": "Identifiants incorrects."}

    if bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return {"status": "ok", "username": username, "full_name": user.full_name}
    else:
        return {"status": "error", "message": "Identifiants incorrects."}