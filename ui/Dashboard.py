import os
import sys

import pandas as pd
import streamlit as st


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.reset_data import reset_and_seed_database

from app.crud import get_all_employees, get_all_clients, get_all_payment, \
    get_all_payslip, get_recent_payment_history

from app.database import SessionLocal

st.set_page_config(page_title="ERP Dashboard", page_icon="📊", layout="wide")

st.title("📊 Enterprise Resource Planning - Dashboard")
st.markdown("---")

db = SessionLocal()

# uncomment for reset the data
# st.markdown("---")
# st.subheader("🛠️ Zone de Maintenance Administrateur")
#
# if st.button("🔴 Réinitialiser et Réinjecter les Données (Seed)", type="primary"):
#     from data.reset_data import reset_and_seed_database
#     try:
#         reset_and_seed_database()
#         st.success("🎯 La base de données a été purgée et recréée avec succès !")
#     except Exception as ex:
#         st.error(f"Erreur lors du reset : {ex}")

try:
    employees = get_all_employees(db)
    clients = get_all_clients(db)
    payments = get_all_payment(db)
    payslips = get_all_payslip(db)

    total_employees = len(employees)

    total_revenue = sum(p.amount for p in payments if p.status == "Paid")
    pending_revenue = sum(p.amount for p in payments if p.status == "Pending")
    total_payroll = sum(e.base_salary for e in employees)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Workforce", f"{total_employees} Staff")
    with col2:
        st.metric("Monthly Payroll (Gross)", f"${float(total_payroll):,.2f}")
    with col3:
        st.metric("Total Revenue", f"${float(total_revenue):,.2f}", delta="Income")
    with col4:
        st.metric(
            "Pending Invoices",
            f"${float(pending_revenue):,.2f}",
            delta="-Unpaid",
            delta_color="inverse",
        )

    st.markdown("---")

    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("👥 Employee Distribution by Title")
        if employees:
            df_emp = pd.DataFrame([{"Job": e.job_title} for e in employees])
            job_counts = df_emp["Job"].value_counts()
            st.bar_chart(job_counts)
        else:
            st.info("No employee data available.")

    with right_chart:
        st.subheader("💰 Payment Status Distribution")
        if payments:
            df_pay = pd.DataFrame(
                [{"Status": p.status, "Amount": float(p.amount)} for p in payments]
            )
            status_summary = df_pay.groupby("Status")["Amount"].sum()
            st.bar_chart(status_summary)
        else:
            st.info("No payment history available.")

    st.markdown("---")

    st.subheader("🚀 Recent Activity Summary")
    tab1, tab2 = st.tabs(["Latest Employees", "Recent Payments"])

    with tab1:
        emp_data = [
            {
                "Employee Name": e.name,
                "Position": e.job_title,
                "Base Salary": f"${float(e.base_salary):,.2f}",
            }
            for e in employees[-5:]
        ]
        st.dataframe(pd.DataFrame(emp_data), width="stretch")

    with tab2:
        pay_recent = []
        recent_records = get_recent_payment_history(db, limit=5)

        for payment, client in recent_records:
            pay_recent.append(
                {
                    "Company Name": (
                        client.company_name
                        if client
                        else f"Unknown (ID: {payment.client_id})"
                    ),
                    "Amount From Client": f"${float(payment.amount):,.2f}",
                    "Invoice Status": payment.status,
                }
            )
        st.dataframe(pd.DataFrame(pay_recent), width="stretch")

    st.markdown("---")
    st.subheader("🛠️ Zone de Maintenance Administrateur")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
finally:
    db.close()

st.sidebar.success("Select a module above to manage data.")
