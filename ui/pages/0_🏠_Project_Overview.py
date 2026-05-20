import streamlit as st
import os
import sys
from sqlalchemy import select
from decimal import Decimal

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Employee, SalaryRule, Payslip
from app.utils.pdf_generator import generate_payslip_pdf

st.set_page_config(page_title="Project Overview & Payroll Engine", layout="wide")

st.title("🏠 Project Overview & Dynamic Payroll Calculation")
st.markdown("---")

db = SessionLocal()

try:
    employees = list(db.execute(select(Employee)).scalars().all())
    rules = list(db.execute(select(SalaryRule)).scalars().all())

    if not employees:
        st.warning(
            "⚠️ No employees found in the database. Please run `reset_data.py` first."
        )
    else:
        st.subheader("⚡ Live Payroll Test Bench")

        selected_emp_name = st.selectbox(
            "Select Employee for Payroll Simulation", [e.name for e in employees]
        )
        emp = next(e for e in employees if e.name == selected_emp_name)

        col_info1, col_info2 = st.columns([2, 1])

        with col_info1:
            st.markdown(f"📊 **Full Position Title:** \n{emp.job_title}")

        with col_info2:
            st.markdown(
                f"💵 **Contract Base Salary:** \n${float(emp.base_salary):,.2f}"
            )

        st.markdown("---")
        st.subheader("🛠️ Customize Payroll Rules for this Period")

        allowance_rules = [r for r in rules if r.category == "allowance"]
        deduction_rules = [r for r in rules if r.category == "deduction"]

        col_rules1, col_rules2 = st.columns(2)

        with col_rules1:
            st.markdown("🍏 **Select Allowances (Primes / Bonus)**")
            allowance_options = {
                f"{r.name} (+{float(r.rate)*100:.1f}%)": r for r in allowance_rules
            }
            selected_allowances = st.multiselect(
                "Active Allowances",
                options=list(allowance_options.keys()),
                default=list(allowance_options.keys()),
            )

        with col_rules2:
            st.markdown("🍎 **Select Deductions (Taxes / Retenues)**")
            deduction_options = {
                f"{r.name} (-{float(r.rate)*100:.1f}%)": r for r in deduction_rules
            }
            selected_deductions = st.multiselect(
                "Active Deductions",
                options=list(deduction_options.keys()),
                default=list(deduction_options.keys()),
            )

        st.markdown(" ")

        if st.button("💸 Compute Live Payslip & Save Transaction", type="primary"):

            base_salary = emp.base_salary
            total_allowances = Decimal("0.00")
            total_deductions = Decimal("0.00")

            for rule_name in selected_allowances:
                rule_obj = allowance_options[rule_name]
                total_allowances += base_salary * rule_obj.rate

            for rule_name in selected_deductions:
                rule_obj = deduction_options[rule_name]
                total_deductions += base_salary * rule_obj.rate

            total_gross = base_salary + total_allowances
            total_net = total_gross - total_deductions

            payslip = Payslip()
            payslip.employee_id = emp.id
            payslip.total_gross = total_gross
            payslip.total_net = total_net

            db.add(payslip)
            db.commit()
            db.refresh(payslip)

            st.info("### Calculation Breakdown Results")
            res_col1, res_col2, res_col3 = st.columns(3)

            res_col1.metric(
                "Calculated Gross Salary", f"${float(payslip.total_gross):,.2f}"
            )
            res_col2.metric(
                "Total Retained Deductions",
                f"${float(total_deductions):,.2f}",
                delta="-Taxes",
                delta_color="inverse",
            )
            res_col3.metric(
                "Final Net Payout Amount", f"${float(payslip.total_net):,.2f}"
            )

            raw_pdf_data = generate_payslip_pdf(employee=emp, payslip=payslip)
            pdf_bytes = bytes(raw_pdf_data)

            st.download_button(
                label="📥 Download Official PDF Payslip",
                data=pdf_bytes,
                file_name=f"payslip_{emp.name.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )
            st.success(f"✨ Custom payroll transaction archived for {emp.name}!")

except Exception as e:
    st.error(f"Error executing payroll engine simulation: {e}")
finally:
    db.close()
