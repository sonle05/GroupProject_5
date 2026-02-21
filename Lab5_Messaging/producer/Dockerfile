FROM python:3.9-slim
RUN pip install pika
WORKDIR /app
COPY send.py .
CMD ["python", "send.py"]