import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3
import os

# Initialize connection to SQLite database
conn = sqlite3.connect('baby_fundraiser.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''
    CREATE TABLE IF NOT EXISTS predictions
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     name TEXT,
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

# Function to save predictions to CSV
def save_to_csv():
    predictions = pd.read_sql_query("SELECT * FROM predictions", conn)
    predictions.to_csv('predictions.csv', index=False)

st.title("Baby Fundraiser Pool: Steph and Aoife")

# ... [rest of the page content remains the same] ...

if st.button("Submit Predictions"):
    if user_name:
        # Save data to SQLite database
        c.execute('''
            INSERT INTO predictions (name, steph_gender, steph_weight, steph_hair, steph_date,
                              aoife_gender, aoife_weight, aoife_hair, aoife_date,
                              born_first, combined_weight, total_length)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_name, steph_gender, steph_weight, steph_hair, steph_date,
              aoife_gender, aoife_weight, aoife_hair, aoife_date,
              born_first, combined_weight, total_length))
        conn.commit()
        
        # Save to CSV after each new prediction
        save_to_csv()
        
        st.success("Thank you for your predictions! Your submission has been saved.")
        st.info("Remember to make your donation if you haven't already!")
    else:
        st.error("Please enter your name before submitting.")

# Display current predictions
st.subheader("Current Predictions")
predictions = pd.read_sql_query("SELECT * FROM predictions", conn)
st.dataframe(predictions)

# Close the database connection
conn.close()

st.markdown("""
---
For any questions or issues, please contact: mark.kirkpatrick@aecom.com
""")

# Add a download button for the CSV file
if os.path.exists('predictions.csv'):
    with open('predictions.csv', 'rb') as file:
        st.download_button(
            label="Download Predictions CSV",
            data=file,
            file_name='predictions.csv',
            mime='text/csv'
        )
