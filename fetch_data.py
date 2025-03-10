import pymysql
import pandas as pd
import matplotlib.pyplot as plt

# Database connection details
db_config = {
    "host": "project.cqlcucieez19.us-east-1.rds.amazonaws.com",
    "user": "admin",
    "password": "Princep1999$",  # Use your actual password
    "database": "project"
}

# Connect to MySQL
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# Fetch data from user table
query_users = "SELECT * FROM user;"
cursor.execute(query_users)
user_data = cursor.fetchall()

# Fetch data from visitor table
query_visitors = "SELECT * FROM visitor;"
cursor.execute(query_visitors)
visitor_data = cursor.fetchall()

# Convert to DataFrame
df_users = pd.DataFrame(user_data, columns=["user_id", "name"])
df_visitors = pd.DataFrame(visitor_data, columns=["user_id", "purpose"])

# Save as CSV (optional)
df_users.to_csv("users.csv", index=False)
df_visitors.to_csv("visitors.csv", index=False)

# Close connection
cursor.close()
conn.close()

print("✅ Data fetched and saved successfully!")
