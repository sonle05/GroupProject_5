import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MYSQL_URL = "mysql+pymysql://root:root@mysql:3306/webstore"

def retry_connection():
    while True:
        try:
            engine = create_engine(MYSQL_URL)
            engine.connect()
            print("✅ Connected to MySQL")
            return engine
        except Exception as e:
            print("⏳ Waiting for MySQL...")
            time.sleep(5)

engine = retry_connection()
SessionLocal = sessionmaker(bind=engine)