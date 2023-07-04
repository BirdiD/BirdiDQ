import streamlit as st
import streamlit.components.v1 as components
from streamlit_extras import *
import pandas as pd
import time
import webbrowser
from utils import * 
from geutils import DataQuality


st.set_page_config(
    page_title="BirdiDQ",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)  
st.title("❄️ BirdiDQ")
st.markdown('<h1 style="font-size: 24px; font-weight: bold; margin-bottom: 0;">Welcome to your DQ App</h1>', unsafe_allow_html=True)

with open("main_birdi/ui/side.md", "r") as sidebar_file:
    sidebar_content = sidebar_file.read()

# Display the DDL for the selected table
st.sidebar.markdown(sidebar_content, unsafe_allow_html=True)


def main():
    # Set the app title
    session_state = st.session_state
    if 'page' not in session_state:
        session_state['page'] = 'home'
    # Select the data source
    mapping, data_owners = get_mapping('main_birdi/data/')
    datasources = list(mapping.keys())
    data_source = st.selectbox("Select the data source", [""]+datasources)

    DQ_APP = None  # Initialize DQ_APP object

    checks_input = None  # Initialize checks_input variable
    if data_source:
        # Display a preview of the data
        st.subheader("Preview of the data:")
        try:
            data = pd.read_csv(f"main_birdi/data/{mapping.get(data_source, None)}")
            filtered_df = dataframe_explorer(data, case=False)
            st.dataframe(filtered_df, use_container_width=True)
        except:
            raise Exception("Sorry, no numbers below zero")

        if DQ_APP is None:  # Create DQ_APP object if not already created
            DQ_APP = DataQuality(data_source, data)
        # Perform data quality checks
        st.subheader("Perform Data Quality Checks")

        checks_input = st.text_area("Describe the checks you want to perform",
                                    placeholder="For instance:  'Check that none of the values in the address column match the pattern for an address starting with a digit'. \n Provide the accurate column name as in the example.")

        # Button to get started
        if checks_input:
            submit_button = st.button("Submit")
            if submit_button:
                with st.spinner('Running your data quality checks'):
                    time.sleep(5)
                    try:
                        nltoge = naturallanguagetoexpectation(checks_input)
                        #st.write(nltoge)
                        expectation_result = DQ_APP.run_expectation(nltoge)
                        #print(expectation_result.to_json_dict())
                        st.success('Your test has successfully been run! Get results')
                        with st.expander("Show Results"):
                            st.subheader("Data Quality result")
                            display_test_result(expectation_result.to_json_dict())
                    except:
                        st.write("Please rephrase sentence")
            col1, col2 = st.columns([1, 1])
            with col1:
                open_docs_button = st.button("Open Data Docs")
                if open_docs_button:
                    # Get the URL to the Data Docs
                    data_docs_url = DQ_APP.context.get_docs_sites_urls()[0]['site_url']
                    st.write(data_docs_url)

                    # Open the URL in the browser
                    webbrowser.open_new_tab(data_docs_url)
            
            with col2:
                if session_state['page'] == 'home':
                        data_owner_button = st.button("Contact Data Owner")
                        if data_owner_button:
                            session_state['page'] = 'contact_form'

                if session_state['page'] == 'contact_form':
                        st.header("Contact Form")
                        sender_email = "annotepulaar@gmail.com"
                        recipient_email = st.text_input("Recipient Email", value=data_owners[data_source])
                        subject = st.text_input("Subject")
                        message = st.text_area("Message")
                        attachement = "main_birdi/uncommitted/data_docs/local_site/index.html"
                        if st.button("Send Email"):
                            send_email_with_attachment(sender_email, recipient_email, subject, message, attachement)
                            session_state['page'] = 'email_sent'
                            
            if session_state['page'] == 'email_sent':
                session_state['page'] = 'home'

local_css("main_birdi/ui/front.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
remote_css('https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@300;400;500;600;700&display=swap')
# Run the app
if __name__ == "__main__":
    main()
