from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
import uvicorn

# Import các cấu hình từ file database.py và rabbitmq.py của nhóm
from database import SessionLocal, engine
from rabbitmq import publish_order

app = FastAPI(title="Noah Order API")

# Schema dữ liệu đầu vào
class OrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# Dependency để quản lý Session Database (Đảm bảo đóng kết nối sau khi dùng)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/orders")
def create_order(order: OrderRequest, db: Session = Depends(get_db)):
    # 1. Kiểm tra nghiệp vụ cơ bản
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="Số lượng phải lớn hơn 0")

    try:
        # 2. Insert dữ liệu vào MySQL (Web Store DB)
        query = text("""
            INSERT INTO orders (user_id, product_id, quantity, status)
            VALUES (:user_id, :product_id, :quantity, 'PENDING')
        """)
        
        result = db.execute(query, {
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity
        })
        db.commit()
        
        # Lấy ID đơn hàng vừa tạo
        order_id = result.lastrowid

        # 3. Đẩy thông tin vào RabbitMQ (Async Messaging)
        order_data = {
            "order_id": order_id,
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity,
            "status": "PENDING"
        }
        
        publish_order(order_data)

        return {
            "status": "success",
            "message": "Đơn hàng đã được tiếp nhận và đang chờ xử lý",
            "order_id": order_id
        }

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Lỗi hệ thống: {str(e)}")
        raise HTTPException(status_code=500, detail="Lỗi kết nối cơ sở dữ liệu hoặc Message Broker")

# Chạy server tại port 5000 để khớp với cấu hình Kong
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
