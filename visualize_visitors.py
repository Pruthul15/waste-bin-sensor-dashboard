import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from collections import Counter

# Load visitor data
df_visitors = pd.read_csv("visitors.csv")

# Count word occurrences in visitor purposes
all_purposes = " ".join(df_visitors["purpose"]).split()
word_counts = Counter(all_purposes)

# Select top 5 most common words
top_words = dict(word_counts.most_common(5))

# Create pie chart
plt.figure(figsize=(6, 6))
plt.pie(top_words.values(), labels=top_words.keys(), autopct="%1.1f%%", colors=["red", "blue", "green", "purple", "orange"])
plt.title("Top Visitor Purposes")
plt.show()
