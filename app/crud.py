import os
import re
import sys
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Row, delete, select
from sqlalchemy.orm import Session


from app.exceptions import (
    DuplicatePayslipError,
    DuplicateRuleError,
    NegativeAmountError,
    ValidationError,
)
from app.models import Client, Employee, PaymentHistory, Payslip, SalaryRule


## Employee
def create_employee(
    db: Session, name: str, job_title: str, base_salary: Decimal
) -> Employee:
    if base_salary <= Decimal("0.00"):
        raise ValidationError("Base contract salary must be strictly positive.")

    new_emp = Employee(name=name, job_title=job_title, base_salary=base_salary)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


def update_employee(
    db: Session, employee_name: str, job_title: str, base_salary: Decimal
) -> Employee | None:
    if base_salary <= Decimal("0.00"):
        raise ValidationError("Updated salary parameters must be positive.")

    emp_to_update = db.execute(
        select(Employee).where(Employee.name == employee_name)
    ).scalar_one_or_none()

    if emp_to_update:
        emp_to_update.job_title = job_title
        emp_to_update.base_salary = base_salary
        db.commit()
        db.refresh(emp_to_update)
    return emp_to_update


def delete_employee(db: Session, employee_name: str) -> bool:
    emp_to_delete = db.execute(
        select(Employee).where(Employee.name == employee_name)
    ).scalar_one_or_none()

    if emp_to_delete:
        db.execute(
            delete(Payslip).where(Payslip.employee_id == emp_to_delete.id)
        )
        db.delete(emp_to_delete)
        db.commit()
        return True
    return False


def get_employee_payroll_history(db: Session, employee_id: int) -> list[Payslip]:
    result = db.execute(
        select(Payslip)
        .where(Payslip.employee_id == employee_id)
        .order_by(Payslip.date_generated.desc())
    )
    return list(result.scalars().all())


def get_employee_by_name(db: Session, employee_name: str) -> Employee | None:
    result = db.execute(select(Employee).where(Employee.name == employee_name))
    return result.scalar_one_or_none()


def get_all_employees(db: Session) -> list[Employee]:
    result = db.execute(select(Employee).order_by(Employee.name))
    return list(result.scalars().all())


## Client
def create_client(
    db: Session, name: str, company_name: str, email: str
) -> Client:
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    clean_email = email.strip() if email else ""

    if not re.match(email_regex, clean_email):
        raise ValidationError(
            f"The email address '{email}' is invalid. "
            f"It must follow a standard format (e.g., user@company.com)."
        )

    new_client = Client(name=name, company_name=company_name, email=clean_email)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


def get_all_clients(db: Session) -> list[Client]:
    result = db.execute(select(Client).order_by(Client.name))
    return list(result.scalars().all())


## Payment
def create_payment(
    db: Session, client_id: int, amount: Decimal, status: str
) -> PaymentHistory:
    if amount <= Decimal("0.00"):
        raise NegativeAmountError(
            "A customer payment amount must be strictly greater than $0.00."
        )

    new_payment = PaymentHistory(
        client_id=client_id, amount=amount, status=status
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


def get_client_payment_history(
    db: Session, client_id: int
) -> list[PaymentHistory]:
    result = db.execute(
        select(PaymentHistory)
        .where(PaymentHistory.client_id == client_id)
        .order_by(PaymentHistory.date_paid.desc())
    )
    return list(result.scalars().all())


def get_all_payment(db: Session) -> list[PaymentHistory]:
    result = db.execute(select(PaymentHistory))
    return list(result.scalars().all())


def get_recent_payment_history(
    db: Session, limit: int = 5
) -> list[tuple[PaymentHistory, Client]]:
    stmt = (
        select(PaymentHistory, Client)
        .join(Client, PaymentHistory.client_id == Client.id, isouter=True)
        .order_by(PaymentHistory.id.desc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


## PaySlip
def get_all_payslip(db: Session) -> list[Payslip]:
    result = db.execute(select(Payslip))
    return list(result.scalars().all())


def create_payslip(
    db: Session,
    employee_id: int,
    total_gross: Decimal,
    total_net: Decimal,
    period: str = None,
) -> Payslip:
    if period is None:
        period = datetime.now().strftime("%Y-%m")

    existing = db.execute(
        select(Payslip).where(
            Payslip.employee_id == employee_id, Payslip.period == period
        )
    ).scalar_one_or_none()

    if existing:
        raise DuplicatePayslipError(
            f"Employee already has an archived payslip for {period}."
        )

    if total_net < Decimal("0.00"):
        raise ValidationError("The final Net payout amount cannot be negative.")
    if total_net > total_gross:
        raise ValidationError(
            "Incoherent calculation: Net salary cannot exceed Gross salary."
        )

    payslip = Payslip()
    payslip.employee_id = employee_id
    payslip.total_gross = total_gross
    payslip.total_net = total_net
    payslip.period = period

    db.add(payslip)
    db.commit()
    db.refresh(payslip)
    return payslip


## Salary_Rules
def get_all_salary_rules(db: Session) -> list[SalaryRule]:
    result = db.execute(select(SalaryRule).order_by(SalaryRule.name))
    return list(result.scalars().all())


def create_salary_rule(
    db: Session, name: str, category: str, rate: Decimal
) -> SalaryRule:
    existing = db.execute(
        select(SalaryRule).where(SalaryRule.name == name)
    ).scalar_one_or_none()
    if existing:
        raise DuplicateRuleError(f"A salary rule named '{name}' already exists.")

    if rate < Decimal("0.00") or rate > Decimal("1.00"):
        raise NegativeAmountError(
            "The rule rate must be strictly between 0% and 100%."
        )

    new_rule = SalaryRule(name=name, category=category, rate=rate)
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return new_rule


def update_salary_rule_rate(
    db: Session, rule_name: str, new_rate: Decimal
) -> SalaryRule | None:
    if new_rate < Decimal("0.00") or new_rate > Decimal("1.00"):
        raise NegativeAmountError("The rate must be between 0% and 100%.")

    rule = db.execute(
        select(SalaryRule).where(SalaryRule.name == rule_name)
    ).scalar_one_or_none()
    if rule:
        rule.rate = new_rate
        db.commit()
        db.refresh(rule)
    return rule