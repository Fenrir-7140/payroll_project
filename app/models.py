from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, engine


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    job_title: Mapped[str | None] = mapped_column(String, nullable=True)

    base_salary: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )

    payslips: Mapped[list["Payslip"]] = relationship(
        "Payslip", back_populates="employee", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "base_salary > 0.00", name="check_logged_salary_positive"
        ),
    )


class SalaryRule(Base):
    __tablename__ = "salary_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)

    rate: Mapped[Decimal] = mapped_column(Numeric(6, 4))
    category: Mapped[str] = mapped_column(String)

    __table_args__ = (
        CheckConstraint("rate >= 0.0000", name="check_rate_positive"),
        CheckConstraint("rate <= 1.0000", name="check_rate_max"),
        CheckConstraint(
            "category IN ('allowance', 'deduction')",
            name="check_valid_category",
        ),
    )


class Payslip(Base):
    __tablename__ = "payslips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("employees.id")
    )
    date_generated: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    period: Mapped[str] = mapped_column(String, nullable=False)

    total_gross: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    total_net: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2), nullable=True
    )

    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="payslips"
    )

    __table_args__ = (
        CheckConstraint(
            "total_net <= total_gross", name="check_net_le_gross"
        ),
        CheckConstraint("total_net >= 0.00", name="check_net_positive"),
    )


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    company_name: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)


class PaymentHistory(Base):
    __tablename__ = "payment_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("clients.id"), nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String, default="pending")
    date_paid: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint("amount > 0.00", name="check_payment_amount_positive"),
    )


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)