import pandas as pd
import sqlite3

def run_etl():
    print("STARTED ETL PROCESS...")

    print("Extracting data...")

    try:
        df_customers = pd.read_csv("customers.csv")
        print(f"Loaded {len(df_customers)} customers from CSV")
    except Exception as e:
        print("Error reading customers.csv:", e)
        return

    conn = None
    try:
        conn = sqlite3.connect("orders.db")
        df_orders = pd.read_sql_query("SELECT * FROM orders", conn)
        print(f"Loaded {len(df_orders)} orders from database")
    except Exception as e:
        print("Error reading orders.db:", e)
        return
    finally:
        if conn:
            conn.close()

    print("Transforming data...")

    merged_df = pd.merge(
        df_customers,
        df_orders,
        left_on="id",
        right_on="customer_id",
        how="left"
    )

    report_df = (
        merged_df
        .groupby(["name", "email"], as_index=False)["amount"]
        .sum()
    )

    report_df.columns = ["Customer Name", "Email", "Total Spent"]

    print("Loading data...")

    print("\n--- FINAL REPORT ---")
    print(report_df)

    report_df.to_csv("final_report.csv", index=False)
    print("\nReport saved to final_report.csv")

if __name__ == "__main__":
    run_etl()
