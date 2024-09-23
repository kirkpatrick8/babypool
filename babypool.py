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
     total_length REAL,
     submission_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
''')
conn.commit()

# Function to save predictions to CSV
def save_to_csv():
    predictions = pd.read_sql_query("SELECT * FROM predictions", conn)
    predictions.to_csv('predictions.csv', index=False)

st.title("Baby Fundraiser Pool: Steph and Aoife")

st.write("""
## Welcome to the Baby Fundraiser Pool for Steph and Aoife!

We're excited to celebrate the upcoming arrivals of two beautiful babies! 
Steph and Aoife are both due on October 31st, and we're organizing this fundraiser 
to show our love and support by gifting them something special for their new additions.

### How it works:
1. Make a donation to our PayPal pool: [https://www.paypal.com/pools/c/98eafrmTSv](https://www.paypal.com/pools/c/98eafrmTSv)
2. Fill out the form below with your predictions
3. The person with the most accurate predictions wins a prize!

All proceeds will go towards purchasing thoughtful presents for both Steph and Aoife's babies. 
Let's come together to make this a memorable celebration for our friends!

**Remember: This is a fun way to raise money for gifts. No actual betting or gambling is involved.**
""")

st.subheader("Your Predictions")

# Input user's name
user_name = st.text_input("Your Name")

# Create separate forms for each mother
col1, col2 = st.columns(2)

with col1:
    st.subheader("Steph's Baby")
    steph_gender = st.selectbox("Gender (Steph's baby)", ["Boy", "Girl"])
    steph_weight = st.number_input("Weight in pounds (Steph's baby)", min_value=4.5, max_value=11.0, value=7.5, step=0.1)
    steph_hair = st.selectbox("Hair Color (Steph's baby)", ["Blonde", "Brown", "Black", "Red", "No hair"])
    steph_date = st.date_input("Birth Date (Steph's baby)", datetime(2024, 10, 31))

with col2:
    st.subheader("Aoife's Baby")
    aoife_gender = st.selectbox("Gender (Aoife's baby)", ["Boy", "Girl"])
    aoife_weight = st.number_input("Weight in pounds (Aoife's baby)", min_value=4.5, max_value=11.0, value=7.5, step=0.1)
    aoife_hair = st.selectbox("Hair Color (Aoife's baby)", ["Blonde", "Brown", "Black", "Red", "No hair"])
    aoife_date = st.date_input("Birth Date (Aoife's baby)", datetime(2024, 10, 31))

# Who will be born first?
born_first = st.radio("Who will be born first?", ["Steph's baby", "Aoife's baby", "Same day"])

# Additional fun questions
combined_weight = st.number_input("Combined weight of both babies (pounds)", min_value=9.0, max_value=22.0, value=15.0, step=0.1)
total_length = st.number_input("Total length of both babies (inches)", min_value=31.5, max_value=47.0, value=39.0, step=0.5)

st.markdown("""
### Don't forget to donate!
Please visit our [PayPal pool](https://www.paypal.com/pools/c/98eafrmTSv) to make your donation before submitting your predictions.
""")

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
