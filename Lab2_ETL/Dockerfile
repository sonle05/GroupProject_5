# Sử dụng Python Slim 
FROM python:3.9-slim 
 
WORKDIR /app 
 
# Cài đặt thư viện Pandas (Xử lý dữ liệu) 
# Lưu ý: Cài pandas sẽ hơi lâu (1-2 phút) 
RUN pip install pandas sqlalchemy 
 
# Copy toàn bộ code vào COPY . . 
COPY . .
# Chạy script tạo DB trước, sau đó chạy ETL 
CMD ["python", "etl_script.py"] 
