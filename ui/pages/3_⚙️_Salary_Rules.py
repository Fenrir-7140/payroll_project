import os
import sys
import streamlit as st
import pandas as pd
from sqlalchemy import select
from decimal import Decimal

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.database import SessionLocal
from app.models import SalaryRule


def run_rules_page():
    st.set_page_config(page_title="Salary Rules Management", layout="centered")
    st.title("⚙️ Corporate Salary Rules Registry")
    st.write(
        "Manage, update, or create global allowances (primes) and deductions (taxes)."
    )
    st.markdown("---")

    db = SessionLocal()
    try:
        action = st.radio(
            "Select Operation", ["View & Edit", "Create New Rule"], horizontal=True
        )

        if action == "Create New Rule":
            st.subheader("➕ Create a New Global Rule")
            with st.form("create_rule_form", clear_on_submit=True):
                rule_name = st.text_input(
                    "Rule Name (e.g., Green Bonus, Health Insurance)"
                )
                rule_category = st.selectbox("Category", ["allowance", "deduction"])
                rule_rate = st.number_input(
                    "Default Rate (e.g., 0.05 for 5%)",
                    min_value=0.0,
                    max_value=1.0,
                    step=0.01,
                )

                if st.form_submit_button("Save Rule to System"):
                    if rule_name:
                        new_rule = SalaryRule(
                            name=rule_name,
                            category=rule_category,
                            rate=Decimal(str(rule_rate)),
                        )
                        db.add(new_rule)
                        db.commit()
                        st.success(
                            f"Successfully added rule '{rule_name}' to PostgreSQL!"
                        )
                        st.rerun()
                    else:
                        st.error("Rule Name is mandatory.")

        elif action == "View & Edit":
            st.subheader("📝 Existing System Rules")

            rules = list(db.execute(select(SalaryRule)).scalars().all())

            if not rules:
                st.info("No rules found. Please create one or reset data.")
            else:
                rules_data = [
                    {
                        "ID": r.id,
                        "Name": r.name,
                        "Type": (
                            "🍏 Allowance"
                            if r.category == "allowance"
                            else "🍎 Deduction"
                        ),
                        "Default Rate": f"{float(r.rate) * 100:.1f}%",
                    }
                    for r in rules
                ]
                st.dataframe(pd.DataFrame(rules_data), width="stretch", hide_index=True)

                st.markdown("---")
                st.subheader("✏️ Modify an Existing Rule's Rate")

                rule_to_edit_name = st.selectbox(
                    "Select a rule to update", [r.name for r in rules]
                )
                target_rule = db.execute(
                    select(SalaryRule).where(SalaryRule.name == rule_to_edit_name)
                ).scalar_one_or_none()

                if target_rule:
                    with st.form("update_rule_form"):
                        st.info(
                            f"Modifying global rate for: **{target_rule.name}** ({target_rule.category})"
                        )
                        updated_rate = st.number_input(
                            "New Default Rate (decimal)",
                            min_value=0.0,
                            max_value=1.0,
                            value=float(target_rule.rate),
                            step=0.01,
                        )

                        if st.form_submit_button("Update Global Rate"):
                            target_rule.rate = Decimal(str(updated_rate))
                            db.commit()
                            st.success(
                                f"Global rate for '{target_rule.name}' updated to {updated_rate * 100:.1f}%!"
                            )
                            st.rerun()

    except Exception as e:
        st.error(f"Rules View Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_rules_page()
