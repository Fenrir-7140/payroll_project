from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()


class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    job_title = Column(String)
    base_salary = Column(Float, default=0.0)

    # Relation : Un employé peut avoir plusieurs fiches de paie
    payslips = relationship("Payslip", back_populates="employee")


class SalaryRule(Base):
    __tablename__ = 'salary_rules'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)  # ex: "Cotisation Retraite"
    code = Column(String, unique=True)  # ex: "RET_01"
    rate = Column(Float)  # ex: 0.07 pour 7%
    category = Column(String)  # ex: "deduction" ou "contribution"


class Payslip(Base):
    __tablename__ = 'payslips'

    id = Column(Integer, primary_key=True)
    employee_id = Column(Integer, ForeignKey('employees.id'))
    date_generated = Column(DateTime, default=datetime.utcnow)

    total_gross = Column(Float)  # Salaire Brut
    total_net = Column(Float)  # Salaire Net

    # Relations
    employee = relationship("Employee", back_populates="payslips")