import streamlit as st
import pandas as pd
from datetime import datetime
from github import Github
from github import InputGitTreeElement

# GitHub repository details
GITHUB_TOKEN = st.secrets["github"]["GITHUB_TOKEN"]
REPO_NAME = "kirkpatrick8/babypool"
BRANCH_NAME = "main"
FILE_PATH = "predictions.csv"

# Initialize GitHub client
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)

# Function to load existing predictions
@st.cache_data
def load_predictions():
    try:
        content = repo.get_contents(FILE_PATH, ref=BRANCH_NAME)
        df = pd.read_csv(pd.compat.StringIO(content.decoded_content.decode()))
    except:
        df = pd.DataFrame(columns=['Name', 'Steph Gender', 'Steph Weight', 'Steph Hair', 'Steph Date',
                                   'Aoife Gender', 'Aoife Weight', 'Aoife Hair', 'Aoife Date',
                                   'Born First', 'Combined Weight', 'Total Length', 'Submission Time'])
    return df

# Function to save predictions
def save_prediction(data):
    df = load_predictions()
    df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    
    csv_buffer = df.to_csv(index=False)
    
    branch = repo.get_branch(BRANCH_NAME)
    current_commit_sha = branch.commit.sha

    blob = repo.create_git_blob(csv_buffer, "utf-8")
    element = InputGitTreeElement(path=FILE_PATH, mode='100644', type='blob', sha=blob.sha)

    base_tree = repo.get_git_tree(sha=current_commit_sha)
    tree = repo.create_git_tree([element], base_tree)

    parent = repo.get_git_commit(sha=current_commit_sha)
    commit = repo.create_git_commit(f"Update predictions - {datetime.now()}", tree, [parent])

    ref = repo.get_git_ref(f"heads/{BRANCH_NAME}")
    ref.edit(sha=commit.sha)

# Streamlit app
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

user_name = st.text_input("Your Name")

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
            'Steph Date': steph_date,
            'Aoife Gender': aoife_gender,
            'Aoife Weight': aoife_weight,
            'Aoife Hair': aoife_hair,
            'Aoife Date': aoife_date,
            'Born First': born_first,
            'Combined Weight': combined_weight,
            'Total Length': total_length,
            'Submission Time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_prediction(new_prediction)
        
        st.success("Thank you for your predictions! Your submission has been saved.")
        st.info("Remember to make your donation if you haven't already!")
    else:
        st.error("Please enter your name before submitting.")

st.subheader("Current Predictions")
current_predictions = load_predictions()
st.dataframe(current_predictions)

st.markdown("""
---
For any questions or issues, please contact: mark.kirkpatrick@aecom.com
""")

csv = current_predictions.to_csv(index=False)
st.download_button(
    label="Download Predictions CSV",
    data=csv,
    file_name='predictions.csv',
    mime='text/csv'
)
