FROM python:3.9-slim
# Cài đặt flask để app.py có thể chạy được
RUN pip install flask 
WORKDIR /app
COPY app.py .
CMD ["python", "app.py"]