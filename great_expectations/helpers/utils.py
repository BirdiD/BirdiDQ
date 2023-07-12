import os
import base64
from dotenv import load_dotenv, find_dotenv
import streamlit as st
import plotly.graph_objects as go
from streamlit_extras.let_it_rain import rain
import ssl
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv(find_dotenv())
# Get your SendGrid API key from the environment variable
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')


def display_test_result(result):
    """
    Display GE json expectation output
    """
    # Check if the test was successful
    success = result["success"]

    # Display the test result box
    if success:
        st.success('Your data quality test succeeded!', icon="✅")
        rain(emoji="🎈",
             font_size=54,
             falling_speed=5,
             animation_length="infinite",
            )
    else:
        st.error('Test failed. View data docs for more details or contact Data Owner', icon="🚨")
        
    # Create data for the bar chart
    try:
        labels = ['Element Count', 'Unexpected Count', 'Unexpected Percent']
        values = [result['result']['element_count'], result['result']['unexpected_count'], result['result']['unexpected_percent']]
        colors = ['lightskyblue', 'lightcoral', 'lightgreen']

        # Create a bar chart using Plotly
        fig = go.Figure(data=go.Bar(x=labels, y=values, marker=dict(color=colors)))
        fig.update_layout(title='Data Quality Test Results', xaxis_title='Metrics', yaxis_title='Values')

        # Display the bar chart using Streamlit's Plotly support
        st.plotly_chart(fig)

        # Display other details of the report
        st.subheader("Expectation Type")
        st.write(result['expectation_config']["expectation_type"])

        st.subheader("Partial Unexpected List")
        partial_unexpected_list = result['result']["partial_unexpected_list"]
        if partial_unexpected_list:
            st.write(partial_unexpected_list)
        else:
            st.write("No partial unexpected values found.")
    except:
        pass

def send_email_with_attachment(sender_email, recipient_email, subject, message, attachment_path):
    """
    Create the SendGrid email message
    """
    message = Mail(
        from_email=sender_email,
        to_emails=recipient_email,
        subject=subject,
        plain_text_content=message)

    # Attach the file
    with open(attachment_path, 'rb') as file:
        file_data = file.read()
        file_name = os.path.basename(attachment_path)
        file_type = 'application/octet-stream'
        file_disposition = 'attachment'

        # Encode the file data using Base64
        encoded_file_data = base64.b64encode(file_data).decode('utf-8')
        attachment = Attachment(
            FileContent(encoded_file_data),
            FileName(file_name),
            FileType(file_type),
            Disposition(file_disposition)
        )
        message.attachment = attachment

    try:
        # Send the email using SendGrid API
        sendgrid_client = SendGridAPIClient(sendgrid_api_key)
        response = sendgrid_client.send(message)
        if response.status_code == 202:
            st.success("Email sent successfully!")
        else:
            st.warning("Failed to send email. Status Code:", response.status_code)
    except Exception as e:
        pass
        print("Error sending email:", str(e))


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)


