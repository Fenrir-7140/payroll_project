import os
import sys
import streamlit as st
from sqlalchemy import select
from decimal import Decimal

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.database import SessionLocal
from app.models import Employee
from app.crud import create_employee, update_employee, delete_employee


def run_crud_page():
    st.set_page_config(page_title="Employee Directory", layout="centered")

    st.title("👥 Employee Directory Operations")
    st.write(
        "Manage corporate worker structures, handle onboarding, updates, and terminations."
    )
    st.markdown("---")

    db = SessionLocal()
    try:
        crud_action = st.radio(
            "Select Directory Operation",
            ["Create", "Update", "Delete"],
            horizontal=True,
        )

        if crud_action == "Create":
            st.subheader("Onboard New Employee")
            with st.form("create_form", clear_on_submit=True):
                new_name = st.text_input("Full Name")
                new_title = st.text_input("Job Title")
                new_salary = st.number_input(
                    "Base Contract Salary ($)", min_value=0.0, step=100.0
                )

                if st.form_submit_button("Save Employee Profile"):
                    if new_name:
                        salary_decimal = Decimal(str(new_salary))
                        create_employee(
                            db,
                            name=new_name,
                            job_title=new_title,
                            base_salary=salary_decimal,
                        )
                        st.success(
                            f"Successfully added {new_name} to PostgreSQL system registry!"
                        )
                        st.rerun()
                    else:
                        st.error("Full Name field is strict and mandatory.")

        elif crud_action == "Update":
            st.subheader("Modify Employee Records")

            all_emps = list(db.execute(select(Employee)).scalars().all())
            emp_to_update_name = st.selectbox(
                "Select Profile to Edit", [emp.name for emp in all_emps]
            )

            if emp_to_update_name:
                target_emp = db.execute(
                    select(Employee).where(Employee.name == emp_to_update_name)
                ).scalar_one_or_none()

                with st.form("update_form"):
                    updated_title = st.text_input(
                        "Update Job Title", value=target_emp.job_title
                    )

                    updated_salary = st.number_input(
                        "Update Base Salary ($)",
                        min_value=0.0,
                        value=float(target_emp.base_salary),
                        step=100.0,
                    )

                    if st.form_submit_button("Apply Configuration Changes"):
                        salary_decimal = Decimal(str(updated_salary))
                        update_employee(
                            db,
                            employee_name=emp_to_update_name,
                            job_title=updated_title,
                            base_salary=salary_decimal,
                        )
                        st.success(
                            f"Updated historical profile parameters for {emp_to_update_name}!"
                        )
                        st.rerun()

        elif crud_action == "Delete":
            st.subheader("Offboard/Remove Worker Records")

            all_emps = list(db.execute(select(Employee)).scalars().all())
            emp_to_delete_name = st.selectbox(
                "Select Profile to Remove", [emp.name for emp in all_emps]
            )

            if emp_to_delete_name:
                st.warning(
                    f"⚠️ Warning: This clears all corresponding ledger inputs for {emp_to_delete_name}."
                )
                if st.button("🚨 Confirm Structural Profile Deletion"):
                    if delete_employee(db, employee_name=emp_to_delete_name):
                        st.success(
                            "Employee record completely cleaned out from live database registries."
                        )
                        st.rerun()
                    else:
                        st.error("Target employee entry processing mismatch.")

    except Exception as e:
        st.error(f"Directory CRUD View Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_crud_page()
