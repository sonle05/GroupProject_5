import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

MYSQL_URL = "mysql+pymysql://root:root@mysql:3306/webstore"
POSTGRES_URL = "postgresql://postgres:postgres@postgres:5432/finance"

def retry_connection(url, name):
    while True:
        try:
            engine = create_engine(url)
            engine.connect()
            print(f"✅ Connected to {name}")
            return engine
        except:
            print(f"⏳ Waiting for {name}...")
            time.sleep(5)

mysql_engine = retry_connection(MYSQL_URL, "MySQL")
postgres_engine = retry_connection(POSTGRES_URL, "Postgres")

MySQLSession = sessionmaker(bind=mysql_engine)
PostgresSession = sessionmaker(bind=postgres_engine)