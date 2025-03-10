import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

# AWS RDS Database Connection (Update these with your credentials)
def get_db_connection():
    return pymysql.connect(
        host='project.cqlcucieez19.us-east-1.rds.amazonaws.com',  # Your AWS RDS endpoint
        user="admin",  # Your username
        password="Princep1999$",  # Your MySQL password
        database="Project",  # Your database name
        cursorclass=pymysql.cursors.DictCursor
    )

# Fetch data from MySQL
@st.cache_data
def fetch_data(query):
    connection = get_db_connection()
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    connection.close()
    return pd.DataFrame(data)

# Streamlit UI
st.title("Waste Bin Management Dashboard")

# Query 1: Number of Waste Bins Used Per User
query1 = """
    SELECT User.name, COUNT(DISTINCT ObjectRecognitionObservation.sensor_id) AS bins_used
    FROM User
    JOIN ObjectRecognitionObservation ON User.user_id = ObjectRecognitionObservation.oid
    GROUP BY User.name
    ORDER BY bins_used DESC;
"""
df1 = fetch_data(query1)
st.subheader("Waste Bins Used Per User")
st.bar_chart(df1.set_index("name"))

# Query 2: Contaminated Recycling Bins Count
query2 = "SELECT COUNT(*) AS contaminated_bins FROM RecycleBin WHERE contaminated > 0;"
df2 = fetch_data(query2)
st.subheader("Contaminated Recycling Bins")
st.metric("Total Contaminated Bins", df2["contaminated_bins"].iloc[0])

# Query 3: Waste Bin Usage Heatmap
query3 = """
    SELECT X, Y, COUNT(*) AS usage_count FROM WasteBin
    GROUP BY X, Y;
"""
df3 = fetch_data(query3)
st.subheader("Waste Bin Usage Heatmap")
fig = px.density_heatmap(df3, x='X', y='Y', z='usage_count', color_continuous_scale='Blues')
st.plotly_chart(fig)

# Query 4: Students Incorrectly Using Recycling Bins
query4 = """
    SELECT User.name, COUNT(*) AS incorrect_uses
    FROM User
    JOIN ObjectRecognitionObservation ON User.user_id = ObjectRecognitionObservation.oid
    JOIN WasteBin ON ObjectRecognitionObservation.sensor_id = WasteBin.waste_bin_id
    JOIN RecycleBin ON WasteBin.waste_bin_id = RecycleBin.waste_bin_id
    WHERE ObjectRecognitionObservation.Trash_type NOT IN ('Recyclable')
    GROUP BY User.name
    ORDER BY incorrect_uses DESC;
"""
df4 = fetch_data(query4)
st.subheader("Students Incorrectly Using Recycling Bins")
st.bar_chart(df4.set_index("name"))

# Query 5: Weight of Trash Collected Over Time
query5 = """
    SELECT DATE(timestamp) AS date, SUM(weight) AS total_weight FROM LoadObservation
    GROUP BY date
    ORDER BY date;
"""
df5 = fetch_data(query5)
st.subheader("Total Trash Collected Over Time")
fig2 = px.line(df5, x='date', y='total_weight', title="Trash Collected Over Time")
st.plotly_chart(fig2)

st.write("Dashboard created with Streamlit 🚀")
