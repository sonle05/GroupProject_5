from fastapi import FastAPI
import pandas as pd
from sqlalchemy import create_engine
import time

app = FastAPI()

MYSQL_URL = "mysql+pymysql://root:root@mysql-store:3306/webstore"
POSTGRES_URL = "postgresql://postgres:postgres@postgres-finance:5432/finance"

def retry_connection(db_url):
    for i in range(5):
        try:
            engine = create_engine(db_url)
            engine.connect()
            print("Connected!")
            return engine
        except:
            print("Retry DB...")
            time.sleep(5)
    raise Exception("DB connection failed")

mysql_engine = retry_connection(MYSQL_URL)
postgres_engine = retry_connection(POSTGRES_URL)

@app.get("/api/report")
def get_report():

    orders_query = """
        SELECT id, user_id, product_id, quantity, status
        FROM orders
        LIMIT 20
    """

    payments_query = """
        SELECT order_id, amount
        FROM payments
    """

    orders_df = pd.read_sql(orders_query, mysql_engine)
    payments_df = pd.read_sql(payments_query, postgres_engine)

    merged = pd.merge(
        orders_df,
        payments_df,
        left_on="id",
        right_on="order_id",
        how="left"
    )

    return merged.fillna("").to_dict(orient="records")