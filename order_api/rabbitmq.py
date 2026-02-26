import pika
import time
import json

def get_channel():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='rabbitmq')
            )
            channel = connection.channel()
            channel.queue_declare(queue='order_queue', durable=True)
            print("✅ Connected to RabbitMQ")
            return channel
        except:
            print("⏳ Waiting for RabbitMQ...")
            time.sleep(5)

channel = get_channel()

def publish_order(order_data):
    channel.basic_publish(
        exchange='',
        routing_key='order_queue',
        body=json.dumps(order_data),
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )