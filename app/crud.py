from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Employee, Payslip, Client, PaymentHistory
from decimal import Decimal


def create_employee(
    db: Session, name: str, job_title: str, base_salary: Decimal
) -> Employee:
    new_emp = Employee(name=name, job_title=job_title, base_salary=base_salary)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


def update_employee(
    db: Session, employee_name: str, job_title: str, base_salary: Decimal
) -> Employee | None:
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
        payslips_to_delete = db.execute(
            select(Payslip).where(Payslip.employee_id == emp_to_delete.id)
        ).scalars()
        for p in payslips_to_delete:
            db.delete(p)

        db.delete(emp_to_delete)
        db.commit()
        return True
    return False


def get_employee_payroll_history(db: Session, employee_id: int) -> list[Payslip]:
    result = db.execute(select(Payslip).where(Payslip.employee_id == employee_id))
    return list(result.scalars().all())


def create_client(db: Session, name: str, company_name: str, email: str) -> Client:
    new_client = Client(name=name, company_name=company_name, email=email)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client


def get_all_clients(db: Session) -> list[Client]:
    result = db.execute(select(Client))
    return list(result.scalars().all())


def create_payment(
    db: Session, client_id: int, amount: Decimal, status: str
) -> PaymentHistory:
    new_payment = PaymentHistory(client_id=client_id, amount=amount, status=status)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment


def get_client_payment_history(db: Session, client_id: int) -> list[PaymentHistory]:
    result = db.execute(
        select(PaymentHistory).where(PaymentHistory.client_id == client_id)
    )
    return list(result.scalars().all())
