import pika
import json
import time
from database import MySQLSession, PostgresSession
from sqlalchemy import text

def callback(ch, method, properties, body):
    data = json.loads(body)
    print(f"📦 Processing order {data['order_id']}")

    time.sleep(2)  # simulate payment processing

    pg_db = PostgresSession()
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
    pg_db.commit()

    mysql_db = MySQLSession()
    mysql_db.execute(
        text("""
            UPDATE orders
            SET status='COMPLETED'
            WHERE id=:order_id
        """),
        {"order_id": data["order_id"]}
    )
    mysql_db.commit()

    print(f"✅ Order {data['order_id']} completed")

    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq')
            )
            channel = connection.channel()
            channel.queue_declare(queue='order_queue', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='order_queue', on_message_callback=callback)
            print("🚀 Worker started")
            channel.start_consuming()
        except:
            print("⏳ Waiting for RabbitMQ...")
            time.sleep(5)

if __name__ == "__main__":
    main()