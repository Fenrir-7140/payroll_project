from fpdf import FPDF
from app.models import Employee, Payslip

def generate_payslip_pdf(employee: Employee, payslip: Payslip) -> bytes:
    deductions = payslip.total_gross - payslip.total_net
    date_str = payslip.date_generated.strftime("%d/%m/%Y") if payslip.date_generated else "N/A"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)

    pdf.cell(0, 10, "UNIVERSAL PAYROLL ENGINE - PAYSLIP", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Issued on: {date_str}", ln=True, align="R")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Employee Name: {employee.name}", ln=True)
    pdf.cell(0, 10, f"Job Title: {employee.job_title}", ln=True)
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Earnings & Deductions Summary", ln=True)
    pdf.set_font("Arial", "", 12)

    pdf.cell(100, 10, "Base Contract Salary:", border=0)
    pdf.cell(0, 10, f"${employee.base_salary:,.2f}", border=0, ln=True, align="R")

    pdf.cell(100, 10, "Total Gross Earnings:", border=0)
    pdf.cell(0, 10, f"${payslip.total_gross:,.2f}", border=0, ln=True, align="R")

    pdf.set_text_color(200, 0, 0) # Red for deductions
    pdf.cell(100, 10, "Total Deductions Applied:", border=0)
    pdf.cell(0, 10, f"-${deductions:,.2f}", border=0, ln=True, align="R")

    pdf.set_text_color(0, 128, 0) # Green for net
    pdf.set_font("Arial", "B", 14)
    pdf.cell(100, 15, "NET PAYOUT AMOUNT:", border=0)
    pdf.cell(0, 15, f"${payslip.total_net:,.2f}", border=0, ln=True, align="R")

    return pdf.output()