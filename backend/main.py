from fastapi import FastAPI, UploadFile
import pandas as pd
from io import StringIO

from backend.rules import check_missing_values, check_out_of_range, check_duplicates
from backend.database import SessionLocal, AnalysisRun

app = FastAPI()


@app.post("/analyze")
async def analyze(file: UploadFile):
    content = await file.read()
    df = pd.read_csv(StringIO(content.decode("utf-8")))

    missing = check_missing_values(df)
    duplicates = check_duplicates(df, ignore_columns=["id"])
    if "age" in df.columns:
        outliers = check_out_of_range(df, "age", 0, 120)
    else:
        outliers = pd.DataFrame()

    session = SessionLocal()
    run = AnalysisRun(
        filename=file.filename,
        missing_count=len(missing),
        outlier_count=len(outliers),
        duplicate_count=len(duplicates),
    )
    session.add(run)
    session.commit()
    session.close()

    return {
        "missing": missing.astype(object).where(pd.notnull(missing), None).to_dict(orient="records"),
        "outliers": outliers.astype(object).where(pd.notnull(outliers), None).to_dict(orient="records"),
        "duplicates": duplicates.astype(object).where(pd.notnull(duplicates), None).to_dict(orient="records"),
    }


@app.get("/history")
def get_history():
    session = SessionLocal()
    runs = session.query(AnalysisRun).all()
    session.close()

    return [
        {
            "filename": r.filename,
            "timestamp": str(r.timestamp),
            "missing": r.missing_count,
            "outliers": r.outlier_count,
            "duplicates": r.duplicate_count,
        }
        for r in runs
    ]