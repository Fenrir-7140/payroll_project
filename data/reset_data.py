import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from app.database import SessionLocal, engine, Base
from app.models import Employee, SalaryRule, Client, PaymentHistory, Payslip



def reset_and_seed_database():

    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:

        rules = [
            SalaryRule(
                code="BASIC",
                name="Base Contract Allowance",
                rate=Decimal("0.1"),
                category="allowance",
            ),
            SalaryRule(
                code="HEALTH",
                name="Health Insurance Deduction",
                rate=Decimal("0.045"),
                category="deduction",
            ),
            SalaryRule(
                code="PENSION",
                name="State Pension Contribution",
                rate=Decimal("0.07"),
                category="deduction",
            ),
        ]
        db.add_all(rules)
        db.commit()

        employees = [
            Employee(
                name="Alice Vance",
                job_title="Lead Cloud Architect",
                base_salary=Decimal("8500"),
            ),
            Employee(
                name="Bob Miller",
                job_title="Senior Fullstack Engineer",
                base_salary=Decimal("6200"),
            ),
            Employee(
                name="Charlie Day",
                job_title="HR Operations Specialist",
                base_salary=Decimal("4100"),
            ),
        ]
        db.add_all(employees)
        db.commit()

        clients = [
            Client(
                name="Jean Dupont",
                company_name="Acme Corporation",
                email="j.dupont@acme.com",
            ),
            Client(
                name="Sarah Connor",
                company_name="Cyberdyne Systems",
                email="s.connor@cyberdyne.io",
            ),
            Client(
                name="Bruce Wayne",
                company_name="Wayne Enterprises",
                email="bruce@wayne.corp",
            ),
        ]
        db.add_all(clients)
        db.commit()

        acme = (
            db.query(Client).filter(Client.company_name == "Acme Corporation").first()
        )
        cyberdyne = (
            db.query(Client).filter(Client.company_name == "Cyberdyne Systems").first()
        )
        wayne = (
            db.query(Client).filter(Client.company_name == "Wayne Enterprises").first()
        )

        payments = [
            PaymentHistory(
                client_id=acme.id,
                amount=Decimal("15000"),
                status="Paid",
                date_paid=datetime.now(timezone.utc) - timedelta(days=30),
            ),
            PaymentHistory(
                client_id=acme.id,
                amount=Decimal("4500"),
                status="Pending",
                date_paid=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            PaymentHistory(
                client_id=cyberdyne.id,
                amount=Decimal("28900"),
                status="Paid",
                date_paid=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            PaymentHistory(
                client_id=wayne.id,
                amount=Decimal("75000"),
                status="Paid",
                date_paid=datetime.now(timezone.utc) - timedelta(days=45),
            ),
            PaymentHistory(
                client_id=wayne.id,
                amount=Decimal("12500"),
                status="Cancelled",
                date_paid=datetime.now(timezone.utc) - timedelta(days=12),
            ),
        ]

        db.add_all(payments)
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_and_seed_database()
