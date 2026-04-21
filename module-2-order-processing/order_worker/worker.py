import pika
import json
import time
import sys
from database import MySQLSession, PostgresSession
from sqlalchemy import text

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"📦 Processing order {data['order_id']}")

    # Khởi tạo session
    pg_db = PostgresSession()
    mysql_db = MySQLSession()

    try:
        # Giả lập thời gian xử lý (Thanh toán, kiểm tra...)
        time.sleep(2) 

        # 1. Ghi vào PostgreSQL (Hệ thống Tài chính)
        pg_db.execute(
            text("""
                INSERT INTO transactions (order_id, user_id, amount)
                VALUES (:order_id, :user_id, :amount)
            """),
            {
                "order_id": data["order_id"],
                "user_id": data["user_id"],
                "amount": data["quantity"] * 100
            }
        )
        
        # 2. Cập nhật trạng thái trong MySQL (Web Store)
        mysql_db.execute(
            text("""
                UPDATE orders
                SET status='COMPLETED'
                WHERE id=:order_id
            """),
            {"order_id": data["order_id"]}
        )

        # Commit cả hai DB
        pg_db.commit()
        mysql_db.commit()
        
        print(f"✅ Order {data['order_id']} completed and synced.")
        
        # Xác nhận đã xử lý xong tin nhắn
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        # Nếu lỗi, rollback để đảm bảo dữ liệu không bị rác
        pg_db.rollback()
        mysql_db.rollback()
        print(f"❌ Error processing order {data['order_id']}: {str(e)}")
        
        # (Tùy chọn) Requeue=True sẽ đẩy tin nhắn lại vào hàng đợi để thử lại sau
        # ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        
    finally:
        # BẮT BUỘC: Đóng kết nối sau khi xử lý xong mỗi đơn hàng
        pg_db.close()
        mysql_db.close()

def main():
    # Tên host phải khớp với container_name trong docker-compose
    RABBITMQ_HOST = 'message-broker' 
    
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBITMQ_HOST, heartbeat=600)
            )
            channel = connection.channel()
            
            # Khai báo queue (durable=True để không mất queue khi RabbitMQ restart)
            channel.queue_declare(queue='order_queue', durable=True)
            
            # Chỉ nhận 1 tin nhắn mỗi lần để xử lý xong mới lấy tin tiếp theo
            channel.basic_qos(prefetch_count=1)
            
            channel.basic_consume(queue='order_queue', on_message_callback=callback)
            
            print("🚀 Worker is running. Waiting for orders...")
            channel.start_consuming()
            
        except pika.exceptions.AMQPConnectionError:
            print("⏳ RabbitMQ chưa sẵn sàng, đang thử lại sau 5 giây...")
            time.sleep(5)
        except Exception as e:
            print(f"❗ Lỗi không xác định: {e}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("停止 Worker...")
        sys.exit(0)
