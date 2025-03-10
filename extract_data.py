import mysql.connector

# Database connection details
db_config = {
    "host": "project.cqlcucieez19.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "Princep1999$",  # Update if needed
    "database": "project"
}

try:
    # Connect to MySQL
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Fetch data from user table
    query_users = "SELECT * FROM user;"
    cursor.execute(query_users)
    user_data = cursor.fetchall()

    # Fetch data from visitor table
    query_visitors = "SELECT * FROM visitor;"
    cursor.execute(query_visitors)
    visitor_data = cursor.fetchall()

    # Print user data
    print("📌 User Table Data:")
    for row in user_data:
        print(row)

    # Print visitor data
    print("\n📌 Visitor Table Data:")
    for row in visitor_data:
        print(row)

    # Close connection
    cursor.close()
    conn.close()

    print("\n✅ Data fetched and printed successfully!")
except Exception as e:
    print(f"❌ Error: {e}")