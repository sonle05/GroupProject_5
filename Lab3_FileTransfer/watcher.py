import os
import time
import shutil
import csv

# Cấu hình đường dẫn cho Docker
INPUT_DIR = '/app/input'
PROCESSED_DIR = '/app/processed'
ERROR_DIR = '/app/error'

def process_file(filepath):
    print(f"⚡ Found new file: {filepath}")
    filename = os.path.basename(filepath)
    
    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            print(" --- READING DATA ---")
            
            for row in reader:
                # 1. Sử dụng try-catch cho từng dòng (Thử thách nâng cao)
                try:
                    sku = row['sku']
                    qty = int(row['qty']) # Chuyển đổi có thể gây lỗi
                    
                    if qty < 0:
                        raise ValueError(f"Stock cannot be negative: {qty}")
                    
                    # 3. Nếu dòng đúng -> In ra "Updated"
                    print(f" > [Updated] SKU: {sku} | New Qty: {qty}")
                
                except Exception as e:
                    # 2. Nếu dòng lỗi -> Ghi log và tiếp tục dòng sau
                    print(f" ❌ [Skipped bad row] in {filename}: {e}")
                    continue

        # 4. Cuối cùng, luôn di chuyển file vào processed
        dest_path = os.path.join(PROCESSED_DIR, filename)
        if os.path.exists(dest_path):
            os.remove(dest_path)
        shutil.move(filepath, dest_path)
        print(f"✅ Success! Moved to {PROCESSED_DIR}")

    except Exception as e:
        # Chỉ lỗi nặng (không mở được file) mới vào đây
        print(f"❌ Critical Error: {e}")
        shutil.move(filepath, os.path.join(ERROR_DIR, filename))

def start_watching():
    print("👀 Watchdog Service Started... Waiting for files in /input")
    # Đảm bảo các thư mục đích tồn tại
    for d in [PROCESSED_DIR, ERROR_DIR]:
        if not os.path.exists(d):
            os.makedirs(d)
            
    while True:
        files = os.listdir(INPUT_DIR)
        for file in files:
            if file.endswith('.csv'):
                process_file(os.path.join(INPUT_DIR, file))
        time.sleep(5)

if __name__ == "__main__":
    start_watching()