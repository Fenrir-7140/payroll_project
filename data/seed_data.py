import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, Employee, SalaryRule, Client, PaymentHistory, Payslip

def seed_database():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(SalaryRule).count() == 0:
            rules = [
                SalaryRule(code="BASIC", name="Base Contract Allowance", rate=1.00, category="allowance"),
                SalaryRule(code="HEALTH", name="Health Insurance Deduction", rate=0.045, category="deduction"),
                SalaryRule(code="PENSION", name="State Pension Contribution", rate=0.07, category="deduction")
            ]
            db.add_all(rules)
            db.commit()

        if db.query(Employee).count() == 0:
            employees = [
                Employee(name="Alice Vance", job_title="Lead Cloud Architect", base_salary=8500.0),
                Employee(name="Bob Miller", job_title="Senior Fullstack Engineer", base_salary=6200.0),
                Employee(name="Charlie Day", job_title="HR Operations Specialist", base_salary=4100.0)
            ]
            db.add_all(employees)
            db.commit()

        if db.query(Client).count() == 0:
            clients = [
                Client(name="Jean Dupont", company_name="Acme Corporation", email="j.dupont@acme.com"),
                Client(name="Sarah Connor", company_name="Cyberdyne Systems", email="s.connor@cyberdyne.io"),
                Client(name="Bruce Wayne", company_name="Wayne Enterprises", email="bruce@wayne.corp")
            ]
            db.add_all(clients)
            db.commit()

        if db.query(PaymentHistory).count() == 0:
            acme = db.query(Client).filter(Client.company_name == "Acme Corporation").first()
            cyberdyne = db.query(Client).filter(Client.company_name == "Cyberdyne Systems").first()
            wayne = db.query(Client).filter(Client.company_name == "Wayne Enterprises").first()

            payments = [
                PaymentHistory(client_id=acme.id, amount=15000.0, status="Paid", date_paid=datetime.now(timezone.utc) - timedelta(days=30)),
                PaymentHistory(client_id=acme.id, amount=4500.0, status="Pending", date_paid=datetime.now(timezone.utc) - timedelta(days=5)),

                PaymentHistory(client_id=cyberdyne.id, amount=28900.0, status="Paid", date_paid=datetime.now(timezone.utc) - timedelta(days=15)),

                PaymentHistory(client_id=wayne.id, amount=75000.0, status="Paid", date_paid=datetime.now(timezone.utc) - timedelta(days=45)),
                PaymentHistory(client_id=wayne.id, amount=12500.0, status="Cancelled", date_paid=datetime.now(timezone.utc) - timedelta(days=12))
            ]
            db.add_all(payments)
            db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error : {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print('seeding database')
    seed_database()