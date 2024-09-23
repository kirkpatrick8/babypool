import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# Initialize connection to SQLite database
conn = sqlite3.connect('baby_pool.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS bets
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     name TEXT,
     donation REAL,
     steph_gender TEXT,
     steph_weight REAL,
     steph_hair TEXT,
     steph_date DATE,
     aoife_gender TEXT,
     aoife_weight REAL,
     aoife_hair TEXT,
     aoife_date DATE,
     born_first TEXT,
     combined_weight REAL,
     total_length REAL)
''')
conn.commit()

st.title("Baby Betting Pool: Steph and Aoife")

st.write("Welcome to the baby betting pool for Steph and Aoife! Both are due on October 31st. Place your bets and help raise money for their baby presents!")

# Input user's name
user_name = st.text_input("Your Name")

# Create separate forms for each mother
col1, col2 = st.columns(2)

with col1:
    st.subheader("Steph's Baby")
    steph_gender = st.selectbox("Gender (Steph's baby)", ["Boy", "Girl"])
    steph_weight = st.number_input("Weight in kg (Steph's baby)", min_value=2.0, max_value=5.0, value=3.5, step=0.1)
    steph_hair = st.selectbox("Hair Color (Steph's baby)", ["Blonde", "Brown", "Black", "Red", "No hair"])
    steph_date = st.date_input("Birth Date (Steph's baby)", datetime(2024, 10, 31))

with col2:
    st.subheader("Aoife's Baby")
    aoife_gender = st.selectbox("Gender (Aoife's baby)", ["Boy", "Girl"])
    aoife_weight = st.number_input("Weight in kg (Aoife's baby)", min_value=2.0, max_value=5.0, value=3.5, step=0.1)
    aoife_hair = st.selectbox("Hair Color (Aoife's baby)", ["Blonde", "Brown", "Black", "Red", "No hair"])
    aoife_date = st.date_input("Birth Date (Aoife's baby)", datetime(2024, 10, 31))

# Who will be born first?
born_first = st.radio("Who will be born first?", ["Steph's baby", "Aoife's baby", "Same day"])

# Additional fun questions
combined_weight = st.number_input("Combined weight of both babies (kg)", min_value=4.0, max_value=10.0, value=7.0, step=0.1)
total_length = st.number_input("Total length of both babies (cm)", min_value=80.0, max_value=120.0, value=100.0, step=0.5)

# Donation amount
donation = st.number_input("Donation amount (€)", min_value=5, step=5)

if st.button("Submit Bet"):
    if user_name:
        # Save data to SQLite database
        c.execute('''
            INSERT INTO bets (name, donation, steph_gender, steph_weight, steph_hair, steph_date,
                              aoife_gender, aoife_weight, aoife_hair, aoife_date,
                              born_first, combined_weight, total_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_name, donation, steph_gender, steph_weight, steph_hair, steph_date,
              aoife_gender, aoife_weight, aoife_hair, aoife_date,
              born_first, combined_weight, total_length))
        conn.commit()
        st.success("Thank you for your bet! Your submission has been saved.")
    else:
        st.error("Please enter your name before submitting.")

# Display current bets
st.subheader("Current Bets")
bets = pd.read_sql_query("SELECT * FROM bets", conn)
st.dataframe(bets)

# Close the database connection
conn.close()
