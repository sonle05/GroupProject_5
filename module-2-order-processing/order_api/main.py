from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import SessionLocal
from rabbitmq import publish_order
from sqlalchemy import text

app = FastAPI()

class OrderRequest(BaseModel):
    user_id: int
    product_id: int
    quantity: int

@app.post("/api/orders")
def create_order(order: OrderRequest):
    
    if order.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be > 0")

    db = SessionLocal()

    result = db.execute(
        text("""
            INSERT INTO orders (user_id, product_id, quantity, status)
            VALUES (:user_id, :product_id, :quantity, 'PENDING')
        """),
        {
            "user_id": order.user_id,
            "product_id": order.product_id,
            "quantity": order.quantity
        }
    )

    db.commit()

    order_id = result.lastrowid

    publish_order({
        "order_id": order_id,
        "user_id": order.user_id,
        "product_id": order.product_id,
        "quantity": order.quantity
    })

    return {
        "message": "Order received",
        "order_id": order_id
    }