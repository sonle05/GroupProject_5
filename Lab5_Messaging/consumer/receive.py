import pika
import time

credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('my_rabbitmq', 5672, '/', credentials)

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    time.sleep(2)
    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    print(" [*] Waiting for RabbitMQ...")
    time.sleep(15) 
    try:
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # 3. THAY ĐỔI: Phải khớp với bên Producer (durable=True)
        channel.queue_declare(queue='task_queue', durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='task_queue', on_message_callback=callback)

        print(' [*] Waiting for orders. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    start_consuming()