from sqlalchemy.orm import Session
from app.models import Employee, SalaryRule, Payslip

def calculate_payroll(employee_id: int, db: Session) -> Payslip:
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise ValueError(f"Employee with the ID {employee_id} was not found.")

    rules = db.query(SalaryRule).all()

    base_salary = employee.base_salary
    total_deductions = 0.0
    total_allowances = 0.0

    for rule in rules:
        if rule.category == "deduction":
            total_deductions += base_salary * rule.rate
        elif rule.category == "allowance":
            total_allowances += base_salary * rule.rate

    total_gross = total_allowances
    total_net = total_gross - total_deductions

    payslip = Payslip(
        employee_id=employee.id,
        total_gross=round(total_gross, 2),
        total_net=round(total_net, 2)
    )

    return payslip