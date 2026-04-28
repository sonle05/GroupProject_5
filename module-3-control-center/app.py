from fastapi import FastAPI
import pandas as pd
from sqlalchemy import create_engine
import time

app = FastAPI()

# Cấu hình URL kết nối với mật khẩu 2011 đã thống nhất
MYSQL_URL = "mysql+pymysql://root:2011@mysql-store:3306/web_store"
POSTGRES_URL = "postgresql://finance_admin:2011@postgres-finance:5432/finance_db"

def retry_connection(db_url):
    """Hàm thử lại kết nối để tránh lỗi khi DB khởi động chậm hơn App"""
    # Tăng số lần thử lên 20 lần để chắc chắn DB đã kịp up
    for i in range(20): 
        try:
            engine = create_engine(db_url)
            # Thử thực hiện một kết nối thực tế để kiểm tra
            with engine.connect() as connection:
                print(f"Connected to {db_url.split('@')[1]}!")
                return engine
        except Exception as e:
            print(f"Retry DB... ({i+1}/20). Lỗi: {e}")
            time.sleep(5)
    # Thay vì raise Exception làm sập app, ta trả về None để xử lý sau
    return None

# Khởi tạo engine (Sẽ thử kết nối khi app start)
mysql_engine = retry_connection(MYSQL_URL)
postgres_engine = retry_connection(POSTGRES_URL)

@app.get("/api/report")
def get_report():
    # BLOCK TRY-EXCEPT để bắt lỗi xử lý dữ liệu hoặc mất kết nối DB giữa chừng
    try:
        if mysql_engine is None or postgres_engine is None:
            return {"status": "error", "message": "Database chưa sẵn sàng. Vui lòng thử lại sau."}

        orders_query = """
            SELECT id, user_id, product_id, quantity, status
            FROM orders
            LIMIT 20
        """

        payments_query = """
            SELECT order_id, amount
            FROM payments
        """

        # Đọc dữ liệu vào DataFrame
        orders_df = pd.read_sql(orders_query, mysql_engine)
        payments_df = pd.read_sql(payments_query, postgres_engine)

        # Xử lý Outliers cơ bản: Đảm bảo quantity và amount là số, nếu lỗi thì bỏ qua dòng đó
        orders_df['quantity'] = pd.to_numeric(orders_df['quantity'], errors='coerce')
        payments_df['amount'] = pd.to_numeric(payments_df['amount'], errors='coerce')

        # Gộp dữ liệu (Merge)
        merged = pd.merge(
            orders_df,
            payments_df,
            left_on="id",
            right_on="order_id",
            how="left"
        )

        # Sửa lỗi dữ liệu trống (fillna) và trả về kết quả
        return {
            "status": "success",
            "data": merged.fillna("").to_dict(orient="records")
        }

    except Exception as e:
        # Nếu có lỗi bất ngờ, trả về thông báo thay vì sập hệ thống
        return {"status": "error", "message": f"Lỗi xử lý báo cáo: {str(e)}"}