# 1. Phải có dòng này đầu tiên (Base Image)
FROM python:3.9-slim

# 2. Thiết lập thư mục làm việc trong Container
WORKDIR /app

# 3. Chép file requirements vào trước để cài đặt
COPY requirements.txt .

# 4. Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# 5. Sau đó mới chép toàn bộ code (app.py, v.v.) vào sau
COPY . .

# 6. Lệnh để chạy ứng dụng của bạn
CMD ["python", "app.py"]