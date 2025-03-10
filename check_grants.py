import mysql.connector
from mysql.connector import Error

try:
    # Connect to the database
    conn = mysql.connector.connect(
        host="project.cqlcucieez19.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Princep1999$",
        database="project"
    )
    if conn.is_connected():
        print("✅ Database connection successful!")

    cursor = conn.cursor()

    # Execute the SHOW GRANTS query
    cursor.execute("SHOW GRANTS FOR 'admin'@'%'")
    grants = cursor.fetchall()

    # Print the grants
    print("📌 Grants for 'admin'@'%':")
    for grant in grants:
        print(grant[0])

    # Close the connection
    cursor.close()
    conn.close()
    print("✅ Connection closed.")
except Error as e:
    print(f"❌ Error: {e}")