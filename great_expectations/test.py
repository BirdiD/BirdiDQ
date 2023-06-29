import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import streamlit as st
import streamlit.components.v1 as components
from utils import *

st.set_page_config(
    page_title="BirdiDQ",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)  
st.title("❄️ BirdiDQ")
st.markdown('<h1 style="font-size: 24px; font-weight: bold; margin-bottom: 0;">Welcome to your DQ App</h1>', unsafe_allow_html=True)

with open("great_expectations/ui/side.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

# Display the DDL for the selected table
st.sidebar.markdown(sidebar_content, unsafe_allow_html=True)

def main():
    session_state = st.session_state
    
    if 'page' not in session_state:
        session_state['page'] = 'home'
    
    if session_state['page'] == 'home':
        data_owner_button = st.button("Contact Data Owner")
        if data_owner_button:
            session_state['page'] = 'contact_form'
    
    if session_state['page'] == 'contact_form':
        st.header("Contact Form")
        sender_email = "annotepulaar@gmail.com"
        recipient_email = st.text_input("Recipient Email")
        subject = st.text_input("Subject")
        message = st.text_area("Message")
        if st.button("Send Email"):
            send_email_with_attachment(sender_email, recipient_email, subject, message)
            session_state['page'] = 'email_sent'
    
    if session_state['page'] == 'email_sent':
        st.success("Email sent successfully!")
    
    # Reset page state if needed
    if session_state['page'] == 'email_sent':
        session_state['page'] = 'home'

#local_css("great_expectations/ui/frontend.css")
local_css("great_expectations/ui/front.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
remote_css('https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@300;400;500;600;700&display=swap')

# Run the app
if __name__ == "__main__":
    main()
