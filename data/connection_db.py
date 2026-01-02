import pymysql.cursors

connection = pymysql.connect(host='localhost',
                             user='rafael',
                             password='F@milia231120',
                             database='finacias',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM finacias.controle_financeira;"
        cursor.execute(sql)
        result = cursor.fetchone()
        print(result)
    connection.commit()