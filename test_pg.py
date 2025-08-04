# test_pg.py
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="splitbill",
        user="hira",
        password="kmzway55AA",
        host="208.87.132.238",
        port="5432"
    )
    print("Connected to PostgreSQL successfully")
    conn.close()
except Exception as e:
    print("Error connecting to PostgreSQL:", e)
