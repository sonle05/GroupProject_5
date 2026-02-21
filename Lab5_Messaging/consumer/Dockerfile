FROM python:3.9-slim
RUN pip install pika
WORKDIR /app
COPY receive.py .
CMD ["python", "receive.py"]