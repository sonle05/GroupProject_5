import pika
import time
import json
import random

credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('my_rabbitmq', 5672, '/', credentials)

def send_orders():
    print(" [*] Waiting for RabbitMQ...")
    time.sleep(15) 
    
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # 1. THAY ĐỔI: durable=True giúp hàng đợi sống sót khi RabbitMQ restart
        channel.queue_declare(queue='task_queue', durable=True)

        for i in range(1, 11):
            order = {"id": i, "customer": f"User_{i}", "amount": random.randint(100, 500)}
            message = json.dumps(order)
            
            # 2. THAY ĐỔI: delivery_mode=2 giúp tin nhắn được lưu xuống đĩa cứng (Persistent)
            channel.basic_publish(
                exchange='',
                routing_key='task_queue', 
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2, 
                )
            )
            
            print(f" [x] Sent Persistent Order #{i}")
            time.sleep(0.5)

        connection.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    send_orders()