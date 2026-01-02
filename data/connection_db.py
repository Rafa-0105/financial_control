import pymysql.cursors
import os
from dotenv import load_dotenv

load_dotenv()

connection = pymysql.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASSWORD'],
    database=os.environ['DB_NAME'],
    charset=os.environ['DB_CHARSET'],
    cursorclass=pymysql.cursors.DictCursor
)

with connection:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM finacias.controle_financeira;"
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
    connection.commit()