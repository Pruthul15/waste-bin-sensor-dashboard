import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# Load user data
df_users = pd.read_csv("users.csv")

# Count number of users
num_users = df_users["user_id"].count()

# Create a bar chart
plt.figure(figsize=(6, 4))
plt.bar(["Users"], [num_users], color="blue")
plt.xlabel("Category")
plt.ylabel("Count")
plt.title("Total Number of Users")
plt.show()
