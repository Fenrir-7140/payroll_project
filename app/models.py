from sqlalchemy import String, Integer, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from decimal import Decimal
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


class SalaryRule(Base):
    __tablename__ = "salary_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True)

    rate: Mapped[Decimal] = mapped_column(Numeric(6, 4))
    category: Mapped[str] = mapped_column(String)


class Payslip(Base):
    __tablename__ = "payslips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("employees.id"))
    date_generated: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    total_gross: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_net: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    employee: Mapped["Employee"] = relationship("Employee", back_populates="payslips")


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


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
