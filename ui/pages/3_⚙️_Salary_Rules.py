import os
import sys
from decimal import Decimal
import pandas as pd
import streamlit as st

from app.exceptions import ValidationError

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from app.crud import (
    create_salary_rule,
    get_all_salary_rules,
    update_salary_rule_rate,
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
                        try:
                            create_salary_rule(
                                db=db,
                                name=rule_name,
                                category=rule_category,
                                rate=Decimal(str(rule_rate)),
                            )
                            st.success(
                                f"Successfully added rule '{rule_name}' to PostgreSQL!"
                            )
                            st.rerun()
                        except ValidationError as error:
                            st.error(f"🛑 Validation Blocked: {error}")
                        except Exception as e:
                            st.error(f"💥 Critical System Error: {e}")
                    else:
                        st.error("Rule Name is mandatory.")

        elif action == "View & Edit":
            st.subheader("📝 Existing System Rules")

            rules = get_all_salary_rules(db)

            if not rules:
                st.info("No rules found. Please create one or reset data.")
            else:
                rules_data = [
                    {
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

                rules_dict = {r.name: r for r in rules}
                rule_to_edit_name = st.selectbox(
                    "Select a rule to update", list(rules_dict.keys())
                )

                target_rule = rules_dict[rule_to_edit_name]

                with st.form("update_rule_form"):
                    st.info(
                        f"Modifying global rate for: **{target_rule.name}** "
                        f"({target_rule.category})"
                    )
                    updated_rate = st.number_input(
                        "New Default Rate (e.g., 0.05 for 5%)",
                        min_value=0.0,
                        max_value=1.0,
                        value=float(target_rule.rate),
                        step=0.01,
                    )

                    if st.form_submit_button("Update Global Rate"):
                        update_salary_rule_rate(
                            db=db,
                            rule_name=rule_to_edit_name,
                            new_rate=Decimal(str(updated_rate)),
                        )
                        st.success(
                            f"Global rate for '{target_rule.name}' "
                            f"updated to {updated_rate * 100:.1f}%!"
                        )
                        st.rerun()

    except Exception as e:
        st.error(f"Rules View Error: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    run_rules_page()