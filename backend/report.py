from fpdf import FPDF
from datetime import datetime


class QualityReport(FPDF):
    def header(self):
        self.set_fill_color(11, 110, 79)
        self.rect(0, 0, 210, 25, style="F")
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 16)
        self.set_xy(10, 8)
        self.cell(0, 10, "Rapport de Qualite des Donnees", ln=True)
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Genere le {datetime.now().strftime('%d/%m/%Y a %H:%M')}", align="C")


def _add_table(pdf, title, rows):
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(11, 110, 79)
    pdf.cell(0, 8, title, ln=True)
    pdf.set_text_color(30, 30, 30)

    if not rows:
        pdf.set_font("Helvetica", "I", 10)
        pdf.cell(0, 6, "Aucune anomalie detectee.", ln=True)
        pdf.ln(4)
        return

    columns = list(rows[0].keys())
    col_width = 190 / len(columns)

    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(244, 251, 247)
    for col in columns:
        pdf.cell(col_width, 7, str(col), border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for row in rows:
        for col in columns:
            value = row.get(col, "")
            pdf.cell(col_width, 7, str(value) if value is not None else "-", border=1)
        pdf.ln()
    pdf.ln(5)


def generate_pdf_report(filename: str, result: dict) -> bytes:
    pdf = QualityReport()
    pdf.add_page()

    pdf.set_text_color(30, 30, 30)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 8, f"Fichier analyse : {filename}", ln=True)
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(11, 110, 79)
    pdf.cell(0, 10, f"Score de qualite : {result['quality_score']} %", ln=True)
    pdf.ln(3)

    total_outliers = sum(len(v) for v in result["outliers_by_column"].values())

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(30, 30, 30)
    pdf.cell(0, 8, "Indicateurs", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 7, f"Valeurs manquantes : {len(result['missing'])}", ln=True)
    pdf.cell(0, 7, f"Valeurs hors seuil (toutes colonnes) : {total_outliers}", ln=True)
    pdf.cell(0, 7, f"Doublons : {len(result['duplicates'])}", ln=True)
    pdf.ln(5)

    _add_table(pdf, "Valeurs manquantes", result["missing"])

    for column, rows in result["outliers_by_column"].items():
        _add_table(pdf, f"Valeurs hors seuil - colonne '{column}'", rows)

    _add_table(pdf, "Doublons", result["duplicates"])

    return bytes(pdf.output())