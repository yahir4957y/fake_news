import psycopg2

def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="fake_news",
        user="postgres",
        password="4957",
        port="5432"
    )