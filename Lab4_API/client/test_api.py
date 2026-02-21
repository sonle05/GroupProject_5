import requests
import time
import sys

# URL của Server trong mạng Docker
# "my_order_service" là tên container server (Domain Name)
API_URL = "http://my_order_service:5000/orders"

def simulate_user():
    print("Client started... Waiting for Server...")
    time.sleep(5) # Chờ Server khởi động xong

    # 1. Tạo đơn hàng giả lập
    payload = {"product": "Laptop Dell", "amount": 1500}

    try:
        print(f"Sending request to: {API_URL}")
        response = requests.post(API_URL, json=payload)
        
        if response.status_code == 201:
            print(f"✅ Success! Server replied: {response.json()}")
        else:
            print(f"❌ Failed: {response.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")
        print("Tip: Check if Server container is running and hostname is correct.")

if __name__ == "__main__":
    simulate_user()