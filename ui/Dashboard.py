import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models import Employee, SalaryRule
from app.engine.calculator import calculate_payroll
from app.utils.pdf_generator import generate_payslip_pdf

def run_payroll_page():
    st.set_page_config(page_title="Payroll Run", layout="centered")
    st.title("📊 Calculate & Archive Payroll")
    st.write("Welcome to the core processing unit of the Universal Payroll Engine.")
    st.markdown("---")

    db = SessionLocal()
    try:
        employees = db.query(Employee).all()
        employee_options = {emp.name: emp.id for emp in employees}

        if not employee_options:
            st.warning("⚠️ No employees available. Please head over to the Employee Directory page to add one.")
            return

        selected_emp_name = st.selectbox("Select Employee for Payroll", list(employee_options.keys()))
        selected_emp_id = employee_options[selected_emp_name]
        emp_record = db.query(Employee).filter(Employee.id == selected_emp_id).first()

        # Sidebar Rule Monitoring
        st.sidebar.header("System Active Rules")
        rules = db.query(SalaryRule).all()
        for rule in rules:
            st.sidebar.text(f"• {rule.code}: {rule.rate * 100:.2f}% ({rule.category})")

        col1, col2 = st.columns(2)
        col1.metric("Job Title", emp_record.job_title)
        col2.metric("Base Salary", f"${emp_record.base_salary:,.2f}")

        if st.button("🔄 Compute Live Payslip", type="primary"):
            payslip = calculate_payroll(employee_id=selected_emp_id, db=db)
            db.add(payslip)
            db.commit()
            st.success("🎉 Payslip calculated and stored safely in PostgreSQL!")
            st.session_state["current_payslip"] = payslip
            st.session_state["current_emp"] = emp_record

        if "current_payslip" in st.session_state and st.session_state["current_emp"].id == selected_emp_id:
            p = st.session_state["current_payslip"]
            e = st.session_state["current_emp"]
            deds = p.total_gross - p.total_net

            st.markdown("#### Payslip Outcome Details")
            res_col1, res_col2, res_col3 = st.columns(3)
            res_col1.metric("Gross", f"${p.total_gross:,.2f}")
            res_col2.metric("Deductions", f"-${deds:,.2f}")
            res_col3.metric("Net Salary", f"${p.total_net:,.2f}")

            pdf_data = generate_payslip_pdf(e, p)
            st.download_button(
                label="📥 Download Official PDF Payslip",
                data=bytes(pdf_data),
                file_name=f"payslip_{e.name.replace(' ', '_').lower()}.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Payroll View Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_payroll_page()