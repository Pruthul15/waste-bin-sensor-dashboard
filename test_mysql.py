import pymysql

print("🔄 Trying to connect manually...")

try:
    conn = pymysql.connect(
        host="project.cqlcucieez19.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Princep1999$",  # Ensure password is correct
        database="project"
    )
    print("✅ Connection successful!")

    # Run a test query
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    print("Databases:", cursor.fetchall())

    # Close the connection
    cursor.close()
    conn.close()
    print("✅ Connection closed.")

except pymysql.MySQLError as err:
    print(f"❌ Error: {err}")
