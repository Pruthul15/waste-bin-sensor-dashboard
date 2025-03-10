import pymysql

def get_db_connection():
    return pymysql.connect(
        host='project.cqlcucieez19.us-east-1.rds.amazonaws.com',
        user="admin",
        password="Princep1999$",
        database="project",
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
    conn.close()
    print("✅ Connection Successful! Tables:", tables)
except pymysql.Error as e:
    print(f"❌ Database Connection Failed: {e.args[0]}, {e.args[1]}")
