import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import time
import random
import webbrowser
from models.gpt_model import naturallanguagetoexpectation
from models.falcon_model import get_expectations, load_peft_model
from helpers.utils import * 
from connecting_data.database.postgresql import *
from connecting_data.filesystem.pandas_filesystem import *
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.no_default_selectbox import selectbox

local_filesystem_path = 'great_expectations/data/'
session_state = st.session_state

#data_owner_button_key = "data_owner_button_1"

st.set_page_config(
    page_title="BirdiDQ",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)  
st.title("❄️ BirdiDQ")
st.markdown('<h1 style="font-size: 24px; font-weight: bold; margin-bottom: 0;">Welcome to your DQ App</h1>', unsafe_allow_html=True)

with open("great_expectations/ui/side.md", "r", encoding="utf-8") as sidebar_file:
    sidebar_content = sidebar_file.read()

# Display the DDL for the selected table
st.sidebar.markdown(sidebar_content, unsafe_allow_html=True)

def display_data_preview(data):
    """
    Display data for quick data exploration
    Params:
        data (DataFrame) : Selected table on which to run DQ checks    
    """
    try:
        filtered_df = dataframe_explorer(data, case=False)
        st.dataframe(filtered_df, use_container_width=True)
    except:
        raise Exception("Unable to preview data")


def perform_data_quality_checks(DQ_APP, key):
    """
    Function to perform data quality checks
    Params:
        DQ_APP (object) : Instanciated class for data quality checks
                          (Data sources : PostgreSQL, Filesystem, etc.)
    """
    st.subheader("Perform Data Quality Checks")
    
    checks_input = st.text_area("Describe the checks you want to perform", key=key.format(name='check_input'),
                                placeholder="For instance:  'Check that none of the values in the address column match the pattern for an address starting with a digit'. \n Provide the accurate column name as in the example.")

    if checks_input:
        submit_button = st.button("Submit", key=key.format(name='submit'))
        if submit_button:
            with st.spinner('Running your data quality checks'):
                time.sleep(10)
                try:
                    model, tknizer = load_peft_model()
                    nltoge = get_expectations(checks_input, model, tknizer)
                    st.write(nltoge)
                    expectation_result = DQ_APP.run_expectation(nltoge)
                    st.success('Your test has successfully been run! Get results')
                    with st.expander("Show Results"):
                        st.subheader("Data Quality result")
                        display_test_result(expectation_result.to_json_dict())
                except:
                    st.write("Unable to succesfully run the query. This may occur if you either have not selected the correct model (finetuned Falcon-7b model) or you mispelled the column name.")

def open_data_docs(DQ_APP, key):
    """
    Open expectation data docs (great expection html output)
    Params:
        DQ_APP (object) : Instanciated class for data quality checks
                          (Data sources : PostgreSQL, Filesystem, etc.)
    """

    open_docs_button = st.button("Open Data Docs", key=key.format(name='data_docs'))
    if open_docs_button:
        try:
            data_docs_url = DQ_APP.context.get_docs_sites_urls()[0]['site_url']
            st.write(data_docs_url)
            webbrowser.open_new_tab(data_docs_url)
        except:
            st.warning('Unable to open html report. Ensure that you have great_expectations/uncommited folder with validations and data_docs/local_site subfolders.', icon="⚠️")



def contact_data_owner(session_state, data_owners, data_source, key):
    """
    Function to contact data owner
    Params:
        session_state : Current session state
        data_owners (dict) : Contains data sources (tables) as dict keys and the data owner email for each data source
        data_source (str) : Selected data source by user on which they want to run data quality checks
    """
    try:
        if session_state['page'] == 'home':
            data_owner_button = st.button("Contact Data Owner", key=key.format(name='do'))
            if data_owner_button:
                session_state['page'] = 'contact_form'

        if session_state['page'] == 'contact_form':
            st.header("Contact Form")
            sender_email = "birdidq@gmail.com"
            recipient_email = st.text_input("Recipient Email", value=data_owners[data_source])
            subject = st.text_input("Subject", key=key.format(name='subject'))
            message = st.text_area("Message", key=key.format(name='message'))
            attachement = "great_expectations/uncommitted/data_docs/local_site/index.html"
                
            if st.button("Send Email", key=key.format(name='email')):
                send_email_with_attachment(sender_email, recipient_email, subject, message, attachement)
                session_state['page'] = 'email_sent'

        if session_state['page'] == 'email_sent':
            session_state['page'] = 'home'
    except:
        st.warning('Unable to send email. Verify the email setup.', icon="⚠️")

def next_steps(DQ_APP, data_owners, data_source, key):
    """
    Actions to take after running data quality checks
    View expectation data docs
    Contact Data Owner by email with data docs as attachment
    """
    st.subheader("What's next ?")
    t1,t2 = st.tabs(['Expectation Data Docs','Get in touch with Data Owner']) 
    with t1:
        open_data_docs(DQ_APP, key)
    with t2:           
        contact_data_owner(session_state, data_owners, data_source, key)


def main():
    # Set the app title
    DQ_APP = None  
    data_owners = None
    data_source = None

    if 'page' not in session_state:
        session_state['page'] = 'home'

    # Select the data connection
    t1,t2 = st.tabs(['Local File System','PostgreSQL']) 

    with t1:
        mapping, data_owners = local_dataowners(local_filesystem_path)
        tables = list(mapping.keys())
        data_source = selectbox("Select table name", tables)

        if data_source:
            key = "filesystem_{name}"
            # Display a preview of the data
            st.subheader("Preview of the data:")
            data = read_local_filesystem_tb(local_filesystem_path, data_source, mapping)
            display_data_preview(data)

            DQ_APP = PandasFilesystemDatasource(data_source, data)
            perform_data_quality_checks(DQ_APP, key)
            next_steps(DQ_APP, data_owners, data_source, key)

    with t2:
        try:
            data_owners = postgresql_data_owners()
            tables = get_pg_tables()
            data_source = selectbox("Select PostgreSQL table", tables)
            if data_source:
                key = "postgresql_{name}"
                # Display a preview of the data
                st.subheader("Preview of the data:")
                data = read_pg_tables(data_source)
                display_data_preview(data)
        
                DQ_APP = PostgreSQLDatasource('pulaar_translation_db', data_source)
                perform_data_quality_checks(DQ_APP, key)
                next_steps(DQ_APP, data_owners, data_source, key)
        except:
            st.warning('Unable to connect to Postgresql. Please verify that you have added your connection string in .env file', icon="⚠️")
            Exception("PostgreSQL Connection error")

 
local_css("great_expectations/ui/front.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')
remote_css('https://fonts.googleapis.com/css2?family=Red+Hat+Display:wght@300;400;500;600;700&display=swap')
# Run the app
if __name__ == "__main__":
    main()
