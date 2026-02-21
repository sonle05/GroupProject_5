import sqlite3 

# Tạo file database giả lập 
conn = sqlite3.connect('orders.db') 
c = conn.cursor() 

# Tạo bảng Orders 
c.execute('''CREATE TABLE IF NOT EXISTS orders 
             (order_id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL)''')  

# Insert dữ liệu mẫu (Khách hàng 1 mua 2 lần, Khách 2 mua 1 lần, Khách 3 không mua) 
data = [ 
    (101, 1, 500.0), 
    (102, 1, 300.0), 
    (103, 2, 1200.0), 
    (104, 4, 150.0) 
] 

c.executemany('INSERT INTO orders VALUES (?,?,?)', data) 

conn.commit() 
conn.close() 

print("Database orders.db created successfully!")