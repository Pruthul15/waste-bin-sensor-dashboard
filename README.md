🗑️ Waste Bin Sensor Dashboard
🚀 A Streamlit-based web dashboard to analyze and manage waste bin sensor data efficiently.

📌 Features
✅ Real-time Insights: Track waste bin usage, recycling rates, and more.
✅ Interactive Dashboard: Visualizes sensor data using Streamlit.
✅ Database Integration: Fetches data from AWS RDS (MySQL) using PyMySQL.
✅ AWS Deployment: Hosted on an Amazon EC2 instance.
✅ GitHub Version Control: Code updates pushed to this repository.

🔹 Step 1:Install Dependencies
pip install -r requirements.txt
🔹 Step 2: Set up Database Connection
Modify the dashboard.py file with your AWS RDS credentials.

🖥️ Deployment on AWS EC2
We successfully deployed the Streamlit dashboard on an EC2 instance following these steps:

1️⃣ Launched an EC2 instance (Amazon Linux 2023, t2.micro).
2️⃣ Configured security groups to allow SSH (22), HTTP (80), HTTPS (443), and Streamlit (---).
3️⃣ Connected to EC2 via SSH:

 Installed Python & Required Packages:
sudo yum update -y
sudo yum install python3 python3-pip -y
pip install streamlit pymysql pandas

Transferred the project files from local to EC2:

Ran the Streamlit app on EC2:
