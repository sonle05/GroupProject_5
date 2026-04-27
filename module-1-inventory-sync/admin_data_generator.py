import csv
import random
import os
import time

def generate_inventory_csv(file_path):
    products = [101, 102, 103, 104, 105]  # ID sản phẩm mẫu
    rows = []
    
    # Tạo 100 dòng dữ liệu
    for _ in range(100):
        # 95% dữ liệu sạch, 5% dữ liệu bẩn
        if random.random() > 0.05:
            product_id = random.choice(products)
            quantity = random.randint(10, 100)
        else:
            # Giả lập dữ liệu lỗi: số âm hoặc định dạng sai
            product_id = random.choice(["ERROR", 999, ""])
            quantity = random.randint(-50, -1)
            
        rows.append([product_id, quantity])

    with open(file_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['product_id', 'quantity'])
        writer.writerows(rows)
    print(f"[INFO] Đã tạo file {file_path} với dữ liệu mẫu.")

if __name__ == "__main__":
    # Đảm bảo thư mục tồn tại
    os.makedirs("app/input", exist_ok=True)
    generate_inventory_csv("app/input/inventory.csv")