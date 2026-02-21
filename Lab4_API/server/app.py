import os
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Đường dẫn file JSON bên trong container (phải khớp với Volume trong docker-compose)
DATA_FILE = "/app/data/orders.json"

def load_orders():
    """Đọc dữ liệu từ file JSON nếu có"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_orders(orders):
    """Ghi dữ liệu vào file JSON"""
    # Đảm bảo thư mục /app/data tồn tại
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(orders, f, indent=4)

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or 'product' not in data or 'amount' not in data:
        return jsonify({"error": "Invalid Data"}), 400

    # 1. Load dữ liệu hiện có từ file
    orders = load_orders()
    
    # 2. Tạo đơn hàng mới
    new_order = {
        "id": len(orders) + 1,
        "product": data['product'],
        "amount": data['amount'],
        "status": "CONFIRMED"
    }
    orders.append(new_order)
    
    # 3. Lưu lại vào file JSON để không bị mất dữ liệu
    save_orders(orders)

    print(f"✅ Đã lưu đơn hàng vào file: {new_order}")
    return jsonify(new_order), 201

@app.route('/orders', methods=['GET'])
def get_orders():
    orders = load_orders()
    return jsonify({"total": len(orders), "data": orders})

if __name__ == '__main__':
    # Chạy trên host 0.0.0.0 để container khác có thể truy cập
    app.run(host='0.0.0.0', port=5000)