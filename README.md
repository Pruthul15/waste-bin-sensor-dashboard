# 🗑️ Smart Waste Management System — Sensor Data Analysis & Dashboard

> **University campus IoT smart bin database — SQL analysis, Python data processing, and interactive Streamlit dashboard deployed on AWS EC2**

---

## 📊 Project Overview

This project analyzes sensor data from a university campus smart waste management system. Smart bins across campus are equipped with IoT sensors that track **who** threw trash, **what type** of trash, and **how full** each bin is. The goal is to identify usage patterns, flag violations, and optimize bin placement and emptying schedules.

| Metric | Value |
|--------|-------|
| Total trash events analyzed | **49,932** |
| Smart bins on campus | **150** (50 Recycle · 50 Landfill · 50 Compost) |
| Users tracked | **200** |
| Database tables | **18** |
| Trash violation rate | **77.7%** of events — wrong bin! |
| Avg events per hour | **~2,000** — campus runs 24/7 |

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Database** | MySQL — 18-table relational schema |
| **Backend / Analysis** | Python, Pandas, PyMySQL |
| **Dashboard** | Streamlit |
| **Cloud** | AWS EC2 (Amazon Linux 2023) + AWS RDS (MySQL) |
| **Version Control** | Git / GitHub |

---

## 📁 Project Structure

```
waste-bin-sensor-dashboard/
│
├── dashboard.py              # Main Streamlit dashboard app
├── fetch_data.py             # Database connection and data fetching
├── extract_data.py           # Data extraction and cleaning
├── extract_all_tables.py     # Pulls all 18 tables from MySQL
├── visualize_users.py        # User behavior visualizations
├── visualize_visitors.py     # Visitor usage pattern analysis
├── check_grants.py           # Database permission verification
├── test_db.py                # Database connection testing
├── test_mysql.py             # MySQL integration tests
├── extracted_tables/         # Exported CSV data from all tables
└── README.md                 # This file
```

---

## 🗄️ Database Schema — 18 Tables

The database models a real IoT smart waste system:

**Users & People:**
`User` → `Student` · `Faculty` · `Staff` · `Visitor`

**Bins & Buildings:**
`WasteBin` → `RecycleBin` · `LandfillBin` · `CompostBin`
`Building` · `Department` · `School`

**Sensors & Observations:**
`Sensor` → `LocationSensor` · `ObjectRecognitionSensor` · `LoadSensor`
`LocationObservation` · `ObjectRecognitionObservation` · `LoadObservation`

---

## 🔍 Key SQL Queries Written

### Basic Queries
```sql
-- Q1: Find users who used a bin in a specific time window
SELECT DISTINCT u.name
FROM User u, LocationSensor ls, LocationObservation lo
WHERE u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp >= '2019-10-26 14:00:00'
AND lo.timestamp <= '2019-10-26 15:00:00';
```

```sql
-- Q4: Find heavy landfill users (more than 100 events)
SELECT u.user_id, u.name, COUNT(*) AS total_events
FROM User u, LocationSensor ls, LocationObservation lo,
     ObjectRecognitionObservation oro, ObjectRecognitionSensor ors, LandfillBin lb
WHERE u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp = oro.timestamp
AND oro.sensor_id = ors.sensor_id
AND ors.Waste_bin_id = lb.waste_bin_id
GROUP BY u.user_id, u.name
HAVING total_events > 100
ORDER BY total_events DESC;
-- Result: 144 users exceeded 100 landfill events
```

### Advanced Queries
```sql
-- Q5: Top 10 users by compost weight WITH ranking
SELECT user_id, SUM(lob.Weight) AS total_weight,
       RANK() OVER (ORDER BY SUM(lob.Weight) DESC) AS user_rank
FROM User u, LocationSensor ls, LocationObservation lo,
     ObjectRecognitionObservation oro, ObjectRecognitionSensor ors,
     CompostBin cb, LoadSensor lsen, LoadObservation lob
WHERE u.user_id = ls.User_id
AND ls.sensor_id = lo.sensor_id
AND lo.timestamp = oro.timestamp
AND oro.sensor_id = ors.sensor_id
AND ors.Waste_bin_id = cb.waste_bin_id
AND cb.waste_bin_id = lsen.Waste_bin_id
AND lsen.sensor_id = lob.sensor_id
GROUP BY u.user_id
ORDER BY user_rank
LIMIT 10;
```

### Role-Based VIEWs (Data Privacy / RBAC)
```sql
-- App Users: Only see available bins inside buildings
CREATE VIEW App_Users AS
SELECT wb.waste_bin_id, wb.X, wb.Y,
  CASE WHEN rb.waste_bin_id IS NOT NULL THEN 'Recycle'
       WHEN lb.waste_bin_id IS NOT NULL THEN 'LandFill'
       WHEN cb.waste_bin_id IS NOT NULL THEN 'Compost'
  END AS type_of_bin
FROM WasteBin wb, Building b
LEFT JOIN RecycleBin rb ON wb.waste_bin_id = rb.waste_bin_id
LEFT JOIN LandfillBin lb ON wb.waste_bin_id = lb.waste_bin_id
LEFT JOIN CompostBin cb ON wb.waste_bin_id = cb.waste_bin_id
WHERE wb.X >= b.boxLowX AND wb.X <= b.boxUpperX
AND wb.Y >= b.boxLowY AND wb.Y <= b.boxUpperY;
```

### Automated TRIGGERS
```sql
-- BEFORE INSERT trigger: Replace bad sensor readings with NULL
CREATE TRIGGER check_erroneous_load
BEFORE INSERT ON LoadObservation
FOR EACH ROW
BEGIN
    DECLARE last_weight INT;
    DECLARE last_time DATETIME;
    DECLARE has_null INT;

    SELECT COUNT(*) INTO has_null
    FROM LoadObservation
    WHERE sensor_id = NEW.sensor_id AND Weight IS NULL;

    SELECT Weight, timestamp INTO last_weight, last_time
    FROM LoadObservation
    WHERE sensor_id = NEW.sensor_id
    ORDER BY timestamp DESC LIMIT 1;

    IF has_null > 0 THEN
        SET NEW.Weight = NULL;
    ELSEIF last_weight IS NOT NULL
        AND DATEDIFF(NEW.timestamp, last_time) <= 1
        AND ABS(NEW.Weight - last_weight) > 1000 THEN
        SET NEW.Weight = NULL;
    END IF;
END;
```

---

## 💡 Key Business Insights Discovered

**1. 77.7% violation rate** — Only 22.3% of trash events were disposed in the correct bin. Landfill bins had the highest misuse (16,384 wrong events).

**2. Campus runs 24/7** — Trash disposal happens evenly across all 24 hours (~2,000 events/hour). No peak time — sensors needed around the clock.

**3. Department 5 is the biggest trash producer** — 4,986 events vs Department 7's 868. Suggests bin placement near Dept 5 buildings needs optimization.

**4. Average bin load is 51% capacity** — Bins average 30,495 units out of 60,000 max. Emptying schedule can be optimized to reduce unnecessary pickups.

**5. Spatial insight** — "Inside bins" identified using coordinate math: bin X,Y coordinates checked BETWEEN building corner coordinates (no GPS needed).

---

## 🚀 How to Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/Pruthul15/waste-bin-sensor-dashboard.git
cd waste-bin-sensor-dashboard

# 2. Install dependencies
pip install streamlit pymysql pandas matplotlib seaborn

# 3. Set up MySQL database
# Load the schema: sql_data_assignment_project.sql into MySQL first

# 4. Update database credentials in dashboard.py
# host, user, password, database

# 5. Run the Streamlit dashboard
streamlit run dashboard.py
```

---

## ☁️ AWS Deployment

The dashboard was deployed on **AWS EC2** with database hosted on **AWS RDS (MySQL)**:

1. Launched EC2 instance (Amazon Linux 2023, t2.micro)
2. Configured security groups — SSH (22), HTTP (80), HTTPS (443), Streamlit (8501)
3. Installed Python, pip, Streamlit, PyMySQL on EC2
4. Connected to AWS RDS MySQL instance for live data
5. Ran Streamlit app as background process on EC2

```bash
# Run on EC2
nohup streamlit run dashboard.py --server.port 8501 &
```

---

## 📋 SQL Features Used

| Feature | Used In |
|---------|---------|
| Multi-table JOINs (7+ tables) | Q1, Q2, Q3, Q4, Q5 |
| GROUP BY + HAVING | Q4 — filter aggregated counts |
| RANK() window function | Q5 — top 10 leaderboard |
| Spatial coordinate matching | Q2 — inside building detection |
| CASE WHEN conditional logic | Q8 — pivot bin types to columns |
| CREATE VIEW (RBAC) | Q6, Q7, Q8 — role-based access |
| BEFORE INSERT TRIGGER | Q9 — bad sensor data validation |
| AFTER INSERT TRIGGER | Q10 — automatic violation logging |
| Subqueries | Q6 — bin availability check |

---

## 👤 Author

**Pruthul Patel**
MS Business and Information Systems — NJIT
[linkedin.com/in/pruthulpatel](https://linkedin.com/in/pruthulpatel) · [github.com/Pruthul15](https://github.com/Pruthul15)

---

*Database schema and sample data provided for academic purposes — CS 331 Database Systems, NJIT*
