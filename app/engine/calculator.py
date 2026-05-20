from sqlalchemy.orm import Session
from app.models import Employee, SalaryRule, Payslip
from decimal import Decimal


def calculate_payroll(employee_id: int, db: Session) -> Payslip:
    employee = db.get(Employee, employee_id)
    if not employee:
        raise ValueError(f"Employee with the ID {employee_id} was not found.")

    rules = db.query(SalaryRule).all()

    base_salary = employee.base_salary

    total_deductions = Decimal("0.00")
    total_allowances = Decimal("0.00")

    for rule in rules:
        if rule.category == "deduction":
            total_deductions += base_salary * rule.rate
        elif rule.category == "allowance":
            total_allowances += base_salary * rule.rate

    total_gross = total_allowances
    total_net = total_gross - total_deductions

    payslip = Payslip()
    payslip.employee_id = employee.id
    payslip.total_gross = total_gross
    payslip.total_deductions = total_deductions
    payslip.total_net = total_net

    return payslip
