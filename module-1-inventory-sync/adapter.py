import os
import time
import shutil
import csv
import mysql.connector

# --- CẤU HÌNH (Khớp với docker-compose.yml đã sửa) ---
INPUT_DIR = '/app/input'
PROCESSED_DIR = '/app/processed'

# Đảm bảo các thư mục tồn tại
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

db_config = {
    'user': 'root',
    'password': 'password',  # Khớp với MYSQL_ROOT_PASSWORD trong compose
    'host': 'mysql_db',      # Tên service trong docker-compose
    'database': 'noah_retail', # Tên DB trong compose
    'port': 3306
}

def get_db_connection():
    """Thử thách Khởi động lạnh: Hàm tự động thử lại kết nối """
    while True:
        try:
            conn = mysql.connector.connect(**db_config)
            print("[SUCCESS] Connected to MySQL database.")
            return conn
        except mysql.connector.Error as err:
            print(f"[RETRY] DB not ready ({err}). Retrying in 5s...")
            time.sleep(5)

def process_file(filepath):
    filename = os.path.basename(filepath)
    print(f"--- Processing file: {filename} ---")
    
    valid_count = 0
    skipped_count = 0
    
    # Mở kết nối 1 lần duy nhất cho toàn bộ file (Tăng hiệu suất)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    # Validate dữ liệu [cite: 35, 36]
                    pid = int(row['product_id'])
                    qty = int(row['quantity'])

                    if qty < 0:
                        print(f"   -> [Skipped] Quantity negative: {qty}")
                        skipped_count += 1
                        continue

                    # Cập nhật Database [cite: 38]
                    # Lưu ý: Cột trong DB phải khớp với init.sql (thường là stock hoặc quantity)
                    query = "UPDATE products SET stock = %s WHERE id = %s"
                    cursor.execute(query, (qty, pid))
                    valid_count += 1

                except (ValueError, KeyError, TypeError) as e:
                    # Thử thách Dữ liệu bẩn: Không để app bị crash [cite: 211, 212]
                    print(f"   -> [Skipped] Invalid format in row: {row}")
                    skipped_count += 1
        
        conn.commit() # Lưu thay đổi sau khi xử lý hết file
        # Định dạng Log chuẩn theo yêu cầu đầu ra 
        print(f"[INFO] Processed {valid_count} records. Skipped {skipped_count} invalid records.")

    except Exception as e:
        print(f"[CRITICAL ERROR] Failed to process file {filename}: {e}")
    finally:
        cursor.close()
        conn.close()

    # Dọn dẹp: Di chuyển file sang thư mục processed [cite: 39, 42]
    dest_path = os.path.join(PROCESSED_DIR, f"{int(time.time())}_{filename}")
    shutil.move(filepath, dest_path)
    print(f"Moved to: {dest_path}")

def start_watching():
    print("Legacy Adapter Service Started... Polling /app/input [cite: 33]")
    while True:
        if os.path.exists(INPUT_DIR):
            files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')]
            for file in files:
                full_path = os.path.join(INPUT_DIR, file)
                process_file(full_path)
        
        # Cơ chế Polling 5-10 giây/lần [cite: 33]
        time.sleep(10)

if __name__ == "__main__":
    start_watching()