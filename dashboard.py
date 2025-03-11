import pymysql
import pandas as pd
import streamlit as st
from decimal import Decimal

# ✅ Cache the DB connection
@st.cache_resource
def get_db_connection():
    return pymysql.connect(
        host='project.cqlcucieez19.us-east-1.rds.amazonaws.com',
        user="admin",
        password="Princep1999$",
        database="project",
        cursorclass=pymysql.cursors.DictCursor
    )

def fetch_data(query):
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
        return pd.DataFrame(data)
    except pymysql.Error as e:
        st.error(f"❌ Query Failed: {e.args[0]}, {e.args[1]}")
        return pd.DataFrame()

# ✅ Queries
query1 = """
SELECT DISTINCT wastebin.waste_bin_id, wastebin.x, wastebin.y, wastebin.capacity
FROM wastebin
JOIN locationobservation ON wastebin.x = locationobservation.x 
                         AND wastebin.y = locationobservation.y
JOIN visitor ON visitor.user_id = locationobservation.sensor_id
WHERE locationobservation.timestamp BETWEEN '2019-10-26 14:00:00' AND '2019-10-26 15:00:00';
"""

query2 = "SELECT COUNT(*) AS missing_weight_values FROM loadobservation WHERE loadobservation.weight IS NULL;"
query3 = """
SELECT building.name, COUNT(wastebin.waste_bin_id) AS total_bins
FROM building
JOIN wastebin ON wastebin.x BETWEEN building.boxLowX AND building.boxUpperX
              AND wastebin.y BETWEEN building.boxLowY AND building.boxUpperY
GROUP BY building.name
ORDER BY total_bins DESC
LIMIT 5;
"""
query4 = """
SELECT 
    (COUNT(recyclebin.waste_bin_id) / (SELECT COUNT(*) FROM wastebin) * 100) AS recycling_bin_percentage
FROM recyclebin;
"""
query5 = """
SELECT user.name, COUNT(DISTINCT locationobservation.sensor_id) AS total_bins_used
FROM user
JOIN locationobservation ON user.user_id = locationobservation.sensor_id
GROUP BY user.name
ORDER BY total_bins_used DESC
LIMIT 5;
"""
query6 = """
SELECT loadobservation.sensor_id, SUM(loadobservation.weight) AS total_weight
FROM loadobservation
GROUP BY loadobservation.sensor_id
ORDER BY total_weight DESC
LIMIT 5;
"""

# ✅ **Streamlit Dashboard UI**
st.title("♻️ Waste Bin Management Dashboard")
st.markdown("🚀 **Real-time Insights on Waste Bin Usage & Management**")

st.divider()  # ✅ Visual Separation

# ✅ **Query 1: Waste Bins Used by Visitors**
st.subheader("🗑️ Waste Bins Used by Visitors (14:00 - 15:00)")
df1 = fetch_data(query1)
if df1.empty:
    st.warning("❌ No Data Found")
else:
    with st.expander("📊 View Waste Bin Usage Data"):
        st.dataframe(df1)

st.divider()

# ✅ **Three Key Metrics in One Row**
col1, col2, col3 = st.columns(3)

# ✅ **Query 2: Missing Weight Values**
df2 = fetch_data(query2)
if not df2.empty:
    col1.metric("⚠️ Missing Weight Values", df2.iloc[0, 0])
else:
    col1.warning("No Missing Data")

# ✅ **Query 3: Building with Most Waste Bins**
df3 = fetch_data(query3)
if not df3.empty:
    col2.success(f"🏢 {df3.iloc[0, 0]}")
    col2.metric("Most Waste Bins", df3.iloc[0, 1])
else:
    col2.warning("No Data")

# ✅ **Query 4: Recycling Bin Percentage**
df4 = fetch_data(query4)
if not df4.empty:
    recycling_percentage = float(df4.iloc[0, 0])  
    col3.metric("♻️ Recycling Bins (%)", round(recycling_percentage, 2))
else:
    col3.warning("No Data")

st.divider()

# ✅ **Query 5: User Who Used the Most Waste Bins**
st.subheader("👤 User Who Used the Most Waste Bins")
df5 = fetch_data(query5)
if df5.empty:
    st.error("❌ No Data Found")
else:
    with st.expander("📊 View User Data"):
        st.table(df5)

st.divider()

# ✅ **Query 6: Sensor That Recorded the Highest Weight**
st.subheader("📟 Sensor That Recorded the Highest Weight")
df6 = fetch_data(query6)
if df6.empty:
    st.error("❌ No Data Found")
else:
    with st.expander("📊 View Sensor Data"):
        st.table(df6)

st.write("🚀 **Dashboard powered by Streamlit** | Data Updated in Real-Time")
