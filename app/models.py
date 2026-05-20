from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base, engine

class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    job_title = Column(String)
    base_salary = Column(Float, default=0.0)

    payslips = relationship("Payslip", back_populates="employee")


class SalaryRule(Base):
    __tablename__ = 'salary_rules'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    code = Column(String, unique=True)
    rate = Column(Float)
    category = Column(String)


class Payslip(Base):
    __tablename__ = 'payslips'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    date_generated = Column(DateTime, default=datetime.now(timezone.utc))

    total_gross = Column(Float)
    total_net = Column(Float)

    employee = relationship("Employee", back_populates="payslips")

class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    company_name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)

class PaymentHistory(Base):
    __tablename__ = 'payment_history'

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default='pending')
    date_paid = Column(DateTime, default=datetime.now(timezone.utc))

if __name__ == "__main__":
    print("Creating tables")
    Base.metadata.create_all(bind=engine)