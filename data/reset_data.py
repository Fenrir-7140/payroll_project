import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import Base, Employee, SalaryRule, Client, PaymentHistory, Payslip
from decimal import Decimal


def reset_and_seed_database():

    Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:

        rules = [
            SalaryRule(
                code="BASIC",
                name="Base Contract Allowance",
                rate=Decimal("1.0000"),
                category="allowance",
            ),
            SalaryRule(
                code="HEALTH",
                name="Health Insurance Deduction",
                rate=Decimal("0.0450"),
                category="deduction",
            ),
            SalaryRule(
                code="PENSION",
                name="State Pension Contribution",
                rate=Decimal("0.0700"),
                category="deduction",
            ),
        ]
        db.add_all(rules)
        db.commit()

        employees = [
            Employee(
                name="Alice Vance",
                job_title="Lead Cloud Architect",
                base_salary=Decimal("8500.00"),
            ),
            Employee(
                name="Bob Miller",
                job_title="Senior Fullstack Engineer",
                base_salary=Decimal("6200.00"),
            ),
            Employee(
                name="Charlie Day",
                job_title="HR Operations Specialist",
                base_salary=Decimal("4100.00"),
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
                amount=Decimal("15000.00"),
                status="Paid",
                date_paid=datetime.now(timezone.utc) - timedelta(days=30),
            ),
            PaymentHistory(
                client_id=acme.id,
                amount=Decimal("4500.00"),
                status="Pending",
                date_paid=datetime.now(timezone.utc) - timedelta(days=5),
            ),
            PaymentHistory(
                client_id=cyberdyne.id,
                amount=Decimal("28900.00"),
                status="Paid",
                date_paid=datetime.now(timezone.utc) - timedelta(days=15),
            ),
            PaymentHistory(
                client_id=wayne.id,
                amount=Decimal("75000.00"),
                status="Paid",
                date_paid=datetime.now(timezone.utc) - timedelta(days=45),
            ),
            PaymentHistory(
                client_id=wayne.id,
                amount=Decimal("12500.00"),
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
