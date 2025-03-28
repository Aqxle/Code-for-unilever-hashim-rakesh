import streamlit as st
from main import main_page
from utils import check_user_existence
import logging
import hashlib
import pandas as pd
import sys

logging.basicConfig(filename="logs.log",
                    filemode='w',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logging.info("AQXLE")

logger = logging.getLogger('Aqxle Test Environment')

user_password = ""
password = ""
# Function to verify credentials
def verify_credentials(username, password):
    try:
        # Verify the user using stored credentials
        cred_df = pd.read_csv("login_credentials.csv", dtype=str)
        user_cred = cred_df[cred_df["Username"] == username]
        user_password = user_cred["Password"].item()
        return  bool(len(user_cred)) and hashlib.sha256(bytes(password, encoding="utf-8")).hexdigest() == str(user_password), username
    
    except Exception as e:
        # file = open("debug.csv", "w")
        # file.write(f"{e}\n")
        # file.close()
        return False, None

# Function to display the login page
def login_page():
    # Set the page title and icon
    st.set_page_config(page_title="Aqxle", page_icon=":speech_balloon:")
    st.title("Aqxle Test Environment")
    
    # Input fields for username and password
    username = st.text_input("Username", value=st.session_state.usr)
    password = st.text_input("Password", type="password", value=st.session_state.pswd)
    
    #Register Button
    if st.button("Register user"):
        import os
        if os.path.exists(f"{os.getcwd()}/login_credentials.csv"):

            if check_user_existence("login_credentials.csv", username):
                st.error("User already exsists! Please Log In")
            else:
                file = open("login_credentials.csv", "a+")
                file.write(f"{username},{hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest()}\n")
                file.close()
                st.success("User Registered successful! Please Log In")
        else:
            file = open("login_credentials.csv", "w+")
            file.write(f"Username,Password\n{username},{hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest()}\n")
            file.close()
            st.success("User Registered successful! Please Log In")
        
        # Clear the input fields
        st.session_state.usr = ""
        st.session_state.pswd = ""
        
    # Login button
    if st.button("Log In"):
        status, st.session_state.usr_id = verify_credentials(username, password)
        if status:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")

# Initialize session state for login status
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.usr = ""
    st.session_state.pswd = ""

# Display the appropriate page based on login status
if st.session_state.logged_in:
    main_page(st.session_state.usr_id)
else:
    login_page()



## DEBUG CODE
# file = open("debug.csv", "w")
#         file.write(f"{}\n")
#         file.close()