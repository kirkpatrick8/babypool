import streamlit as st
import pandas as pd
from datetime import datetime
from github import Github
from github import GithubException
import io

# GitHub repository details
GITHUB_TOKEN = st.secrets["github"]["GITHUB_TOKEN"]
REPO_NAME = "kirkpatrick8/babypool"
BRANCH_NAME = "main"
FILE_PATH = "predictions.csv"

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Function to load existing predictions
@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_predictions():
    try:
        content = repo.get_contents(FILE_PATH, ref=BRANCH_NAME)
        df = pd.read_csv(io.StringIO(content.decoded_content.decode()))
        st.sidebar.write(f"Loaded {len(df)} predictions")
        return df
    except Exception as e:
        st.sidebar.error(f"Error loading predictions: {e}")
        return pd.DataFrame(columns=['Name', 'Steph Gender', 'Steph Weight', 'Steph Hair', 'Steph Date',
                                     'Aoife Gender', 'Aoife Weight', 'Aoife Hair', 'Aoife Date',
                                     'Born First', 'Combined Weight', 'Total Length', 'Submission Time'])

# Function to save prediction
def save_prediction(data):
    try:
        # Convert the new prediction to a DataFrame
        new_df = pd.DataFrame([data])
        
        # Convert DataFrame to CSV string
        csv_string = new_df.to_csv(index=False, header=False)
        
        try:
            # Try to get the existing file
            contents = repo.get_contents(FILE_PATH, ref=BRANCH_NAME)
            
            # Append the new data to the existing file
            updated_content = contents.decoded_content.decode() + '\n' + csv_string
            
            # Update the file in the repository
            repo.update_file(FILE_PATH, f"Append prediction - {datetime.now()}", updated_content, contents.sha, branch=BRANCH_NAME)
        except GithubException as e:
            if e.status == 404:  # File not found, create it
                # If the file doesn't exist, create it with headers and the new data
                headers = ','.join(new_df.columns) + '\n'
                repo.create_file(FILE_PATH, f"Create predictions file - {datetime.now()}", headers + csv_string, branch=BRANCH_NAME)
            else:
                raise e
        
        st.sidebar.success("Saved prediction successfully")
    except Exception as e:
        st.sidebar.error(f"Error saving prediction: {e}")

# Streamlit app
st.title("Baby Gift Pool: Steph and Aoife")

st.write("""
## Welcome to the Baby Gift Pool for Steph and Aoife!

We're excited to celebrate the upcoming arrivals of two  babies! 
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

born_first = st.radio("Who will be born first?", ["Steph's baby", "Aoife's baby", "Same day"])

combined_weight = st.number_input("Combined weight of both babies (pounds)", min_value=9.0, max_value=22.0, value=15.0, step=0.1)
total_length = st.number_input("Total length of both babies (inches)", min_value=31.5, max_value=47.0, value=39.0, step=0.5)

st.markdown("""
### Don't forget to donate!
Please visit our [PayPal pool](https://www.paypal.com/pools/c/98eafrmTSv) to make your donation before submitting your predictions.
""")

if st.button("Submit Predictions"):
    if user_name:
        new_prediction = {
            'Name': user_name,
            'Steph Gender': steph_gender,
            'Steph Weight': steph_weight,
            'Steph Hair': steph_hair,
            'Steph Date': str(steph_date),
            'Aoife Gender': aoife_gender,
            'Aoife Weight': aoife_weight,
            'Aoife Hair': aoife_hair,
            'Aoife Date': str(aoife_date),
            'Born First': born_first,
            'Combined Weight': combined_weight,
            'Total Length': total_length,
            'Submission Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_prediction(new_prediction)
        st.success("Thank you for your predictions! Your submission has been saved.")
        st.info("Remember to make your donation if you haven't already!")
        
        # Force refresh of predictions
        st.cache_data.clear()
    else:
        st.error("Please enter your name before submitting.")

# Display current predictions
st.subheader("Current Predictions")
current_predictions = load_predictions()
st.dataframe(current_predictions)

st.markdown("""
---
For any questions or issues, please contact: mark.kirkpatrick@aecom.com
""")

# Add a download button for the predictions
csv = current_predictions.to_csv(index=False)
st.download_button(
    label="Download Predictions CSV",
    data=csv,
    file_name='predictions.csv',
    mime='text/csv'
)
