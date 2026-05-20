from sqlalchemy.orm import Session
from app.models import Employee, Payslip, Client, PaymentHistory


def create_employee(db: Session, name: str, job_title: str, base_salary: float) -> Employee:
    new_emp = Employee(name=name, job_title=job_title, base_salary=base_salary)
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp

def update_employee(db: Session, employee_name: str, job_title: str, base_salary: float) -> type[Employee] | None:
    emp_to_update = db.query(Employee).filter(Employee.name == employee_name).first()
    if emp_to_update:
        emp_to_update.job_title = job_title
        emp_to_update.base_salary = base_salary
        db.commit()
        db.refresh(emp_to_update)
    return emp_to_update

def delete_employee(db: Session, employee_name: str) -> bool:
    emp_to_delete = db.query(Employee).filter(Employee.name == employee_name).first()
    if emp_to_delete:
        db.query(Payslip).filter(Payslip.employee_id == emp_to_delete.id).delete()
        db.query(Employee).filter(Employee.id == emp_to_delete.id).delete()
        db.commit()
        return True
    return False

def get_employee_payroll_history(db:Session, employee_id: int) -> list[type[Payslip]]:
    pay_roll = db.query(Payslip).filter(Payslip.employee_id == employee_id).all()
    return pay_roll


def create_client(db: Session, name: str, company_name: str, email: str) -> Client:
    new_client = Client(name=name, company_name=company_name, email=email)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    return new_client

def get_all_clients(db: Session) -> list[type[Client]]:
    return db.query(Client).all()

def create_payment(db: Session, client_id: int, amount: float, status: str) -> PaymentHistory:
    new_payment = PaymentHistory(client_id=client_id, amount=amount, status=status)
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

def get_client_payment_history(db: Session, client_id: int) -> list[type[PaymentHistory]]:
    return db.query(PaymentHistory).filter(PaymentHistory.client_id == client_id).all()