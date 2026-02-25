import os
import time
import shutil
import csv
import mysql.connector # [MỚI] Thêm thư viện để kết nối Database

# --- CẤU HÌNH (Lấy từ Lab 3 nhưng giữ nguyên logic đường dẫn) ---
INPUT_DIR = '/app/input'
PROCESSED_DIR = '/app/processed'

# --- [MỚI] Cấu hình kết nối MySQL ---
# Lý do: Module 1 yêu cầu cập nhật tồn kho vào Database thay vì chỉ in ra màn hình.
db_config = {
    'user': 'root',
    'password': 'rootpassword',
    'host': 'db',          # Tên service trong docker-compose
    'database': 'inventory_db',
    'port': 3306
}

def update_database(product_id, quantity):
    """Hàm thực thi SQL Update"""
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # [MỚI] Logic nghiệp vụ: Cộng dồn hoặc Ghi đè số lượng (Ở đây tôi dùng ghi đè theo đề bài)
        query = "UPDATE products SET quantity = %s WHERE product_id = %s"
        cursor.execute(query, (quantity, product_id))
        conn.commit()
        print(f"   -> [DB Success] Updated Product {product_id} to Qty {quantity}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"   -> [DB Error] Failed to update {product_id}: {e}")

def process_file(filepath):
    filename = os.path.basename(filepath)
    print(f"Found new file: {filename}")
    
    valid_count = 0
    skipped_count = 0

    # [CHỈNH SỬA TỪ LAB 3 - TASK 2 & CHALLENGE]
    # Lab 3 gốc: Nếu 1 dòng lỗi -> vứt cả file sang thư mục error[cite: 65].
    # Module 1 yêu cầu: Bỏ qua dòng lỗi, tiếp tục xử lý dòng đúng (Resilience).
    
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f) # Đọc header tự động (product_id, quantity)
        for row in reader:
            try:
                # [CHỈNH SỬA] Mapping theo field của Module 1 (product_id, quantity) 
                # thay vì (sku, qty) của Lab 3 [cite: 31]
                pid = int(row['product_id'])
                qty = int(row['quantity'])

                # [LOGIC MỚI] Validate dữ liệu theo yêu cầu Module 1
                if qty < 0:
                    print(f"   -> [Skipped] Negative quantity for Product {pid}")
                    skipped_count += 1
                    continue # Bỏ qua dòng này, đi tới dòng tiếp theo (không raise Error)

                # Nếu dữ liệu đẹp -> Gọi hàm update DB
                update_database(pid, qty)
                valid_count += 1

            except (ValueError, KeyError) as e:
                # Bắt lỗi format (ví dụ: chữ thay vì số, thiếu cột)
                print(f"   -> [Skipped] Invalid row format: {row}")
                skipped_count += 1

    print(f"[SUMMARY] File {filename}: Processed {valid_count} | Skipped {skipped_count}")

    # [GIỮ NGUYÊN TỪ LAB 3] Move file sang processed sau khi xong [cite: 61]
    # Để tránh việc adapter đọc lại file này vô hạn lần.
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)
        
    shutil.move(filepath, os.path.join(PROCESSED_DIR, filename))
    print(f"Moved {filename} to processed folder.")

def start_watching():
    print("Legacy Adapter Service Started... Waiting for files...")
    while True:
        # [GIỮ NGUYÊN TỪ LAB 3] Cơ chế Polling [cite: 69-77]
        if os.path.exists(INPUT_DIR):
            files = os.listdir(INPUT_DIR)
            for file in files:
                if file.endswith('.csv'):
                    full_path = os.path.join(INPUT_DIR, file)
                    process_file(full_path)
        
        # Nhịp tim hệ thống: Ngủ 5s để không quá tải CPU [cite: 86]
        time.sleep(5)

if __name__ == "__main__":
    # Chờ 1 chút cho Database khởi động xong (Best practice)
    time.sleep(10)
    start_watching()