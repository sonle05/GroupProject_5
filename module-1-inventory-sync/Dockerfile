FROM python:3.9-slim
WORKDIR /app

#Cài đặt thư viện kết nối MySQL
RUN pip install mysql-connector-python

COPY adapter.py .

CMD ["python", "adapter.py"]