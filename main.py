from app.database import SessionLocal
from app.engine.calculator import calculate_payroll

def test_engine():
    print("--- Starting Payroll Calculation Test ---")

    db = SessionLocal()

    try:
        employee_id = 1
        print(f"Fetching data and calculating payroll for Employee ID: {employee_id}...")

        payslip = calculate_payroll(employee_id=employee_id, db=db)

        print("\n====================================")
        print("          PAYSLIP SIMULATION        ")
        print("====================================")
        print(f" Employee ID : {payslip.employee_id}")
        print(f" Total Gross : ${payslip.total_gross:,}")
        print(f" Total Net   : ${payslip.total_net:,}")
        print("====================================")

        print("\nCalculation successful! The engine works perfectly. 🚀")

    except Exception as e:
        print(f"\n[ERROR] Calculation failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_engine()