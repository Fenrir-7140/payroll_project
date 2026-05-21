import os
import sys
from decimal import Decimal
import pandas as pd
import streamlit as st

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.crud import (
    create_payment,
    get_all_clients,
    get_client_payment_history,
)
from app.database import SessionLocal


def run_payment_page():
    st.set_page_config(page_title="Payment History", layout="centered")

    st.title("💰 Customer Payment History")
    st.markdown("---")

    db = SessionLocal()
    try:
        clients = get_all_clients(db)
        client_options = {c.name: c.id for c in clients}

        if not client_options:
            st.warning(
                "⚠️ Please add a customer in the 'Customer Management' "
                "tab first."
            )
        else:
            selected_client_name = st.selectbox(
                "Select a customer", list(client_options.keys())
            )
            selected_client_id = client_options[selected_client_name]

            st.subheader(f"Record a transaction for {selected_client_name}")
            with st.form("payment_form", clear_on_submit=True):
                amount = st.number_input(
                    "Transaction amount ($)", min_value=0.0, step=50.0
                )
                status = st.selectbox(
                    "Payment status", ["Paid", "Pending", "Cancelled"]
                )

                if st.form_submit_button("Confirm transaction"):
                    amount_decimal = Decimal(str(amount))
                    create_payment(
                        db,
                        client_id=selected_client_id,
                        amount=amount_decimal,
                        status=status,
                    )
                    st.success("Transaction recorded!")
                    st.rerun()

            st.markdown("---")
            st.subheader(f"Transaction history - {selected_client_name}")

            payments = get_client_payment_history(db, selected_client_id)

            if not payments:
                st.info("No transactions recorded for this customer.")
            else:
                formatted_payments = [
                    {
                        "Date": p.date_paid.strftime("%d/%m/%Y at %H:%M"),
                        "Amount": f"${float(p.amount):,.2f}",
                        "Status": p.status,
                    }
                    for p in payments
                ]
                df = pd.DataFrame(formatted_payments)

                st.dataframe(df, width="stretch", hide_index=True)

    except Exception as e:
        st.error(f"Payment View Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_payment_page()