from datetime import datetime
from fpdf import FPDF
from app.models import Employee, Payslip
from decimal import Decimal


def generate_payslip_pdf(employee: Employee, payslip: Payslip) -> bytes:
    gross = payslip.total_gross if payslip.total_gross is not None else Decimal("0.00")
    net = payslip.total_net if payslip.total_net is not None else Decimal("0.00")
    deductions = gross - net

    if payslip.date_generated:
        date_str = payslip.date_generated.strftime("%d/%m/%Y")
    else:
        date_str = datetime.now().strftime("%d/%m/%Y")

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
    pdf.cell(
        0,
        10,
        f"Job Title: {employee.job_title if employee.job_title else 'N/A'}",
        ln=True,
    )
    pdf.ln(5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Earnings & Deductions Summary", ln=True)
    pdf.set_font("Arial", "", 12)

    pdf.cell(100, 10, "Base Contract Salary:", border=0)
    pdf.cell(
        0, 10, f"${float(employee.base_salary):,.2f}", border=0, ln=True, align="R"
    )

    pdf.cell(100, 10, "Total Gross Earnings:", border=0)
    pdf.cell(0, 10, f"${float(gross):,.2f}", border=0, ln=True, align="R")

    pdf.set_text_color(200, 0, 0)
    pdf.cell(100, 10, "Total Deductions Applied:", border=0)
    pdf.cell(0, 10, f"-${float(deductions):,.2f}", border=0, ln=True, align="R")

    pdf.set_text_color(0, 128, 0)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(100, 15, "NET PAYOUT AMOUNT:", border=0)
    pdf.cell(0, 15, f"${float(net):,.2f}", border=0, ln=True, align="R")

    return bytes(pdf.output())
