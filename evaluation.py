from fpdf import FPDF

def generate_pdf_report(name, rounds, result, tech_score, hr_score=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Interview Report - {name}", ln=1)
    pdf.cell(200, 10, txt=f"Result: {result}", ln=1)
    pdf.cell(200, 10, txt=f"Rounds: {rounds}", ln=1)
    pdf.cell(200, 10, txt=f"Technical Score: {tech_score}/50", ln=1)
    if hr_score:
        pdf.cell(200, 10, txt=f"HR Score: {hr_score}/30", ln=1)

    pdf.output(f"feedback_reports/{name}_report.pdf")