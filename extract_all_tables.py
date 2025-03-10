import pymysql
import pandas as pd
import os

# Database connection setup
try:
    print("🔄 Connecting to the database...")
    conn = pymysql.connect(
        host="project.cqlcucieez19.us-east-1.rds.amazonaws.com",
        user="admin",
        password="Prince1999$",
        database="project"
    )
    print("✅ Database connection successful!")

    cursor = conn.cursor()

    # Create a folder to save CSVs
    output_folder = "extracted_tables"
    os.makedirs(output_folder, exist_ok=True)
    print(f"📁 Output folder: {output_folder}")

    # Get the list of all tables in the database
    print("🔄 Fetching list of tables...")
    cursor.execute("SHOW TABLES")
    tables = [table[0] for table in cursor.fetchall()]
    print(f"📌 Tables fetched: {tables}")

    if not tables:
        print("❌ No tables found in the database.")
    else:
        print(f"📌 Found {len(tables)} tables in the database: {tables}")

        # Loop through each table and extract data
        for table in tables:
            try:
                print(f"\n🔄 Extracting: {table} ...")

                # Fetch all data from the table
                query = f"SELECT * FROM {table}"
                print(f"🔍 Executing query: {query}")
                cursor.execute(query)
                rows = cursor.fetchall()

                # Get column names
                column_names = [desc[0] for desc in cursor.description]
                print(f"📄 Columns: {column_names}")

                # Check if the table has data
                if not rows:
                    print(f"⚠️ No data found in table: {table}")
                    continue

                # Save data to CSV
                df = pd.DataFrame(rows, columns=column_names)
                csv_filename = os.path.join(output_folder, f"{table}.csv")
                df.to_csv(csv_filename, index=False)

                print(f"✅ Saved to {csv_filename}")
            except Exception as e:
                print(f"❌ Error extracting {table}: {str(e)}")

    # Close the connection
    cursor.close()
    conn.close()
    print("\n✅ All tables processed successfully!")
except Exception as e:
    print(f"❌ Database connection error: {e}")