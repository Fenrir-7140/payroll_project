import os
import sys
import streamlit as st

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database import SessionLocal
from app.crud import create_client, get_all_clients

def run_client_page():
    st.set_page_config(page_title="Client Management", layout="centered")
    st.title("🏢 Client Management")
    st.write("Customer portfolio management and invoicing area")
    st.markdown("---")

    db = SessionLocal()
    try:
        st.subheader("Add a new customer")
        with st.form("client_form", clear_on_submit=True):
            name = st.text_input("Contact's full name")
            company = st.text_input("Company name")
            email = st.text_input("Email address")

            if st.form_submit_button("Register Customer"):
                if name and email:
                    create_client(db, name=name, company_name=company, email=email)
                    st.success(f"Customer '{name}' successfully registered !")
                    st.rerun()
                else:
                    st.error("Name and email are required.")

        st.markdown("---")
        st.subheader("List of existing clients")
        clients = get_all_clients(db)
        if clients:
            for c in clients:
                st.text(f"• {c.name} ({c.company_name}) - {c.email}")
        else:
            st.info("No customers registered at this time.")

    except Exception as e:
        st.error(f"Client View Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    run_client_page()