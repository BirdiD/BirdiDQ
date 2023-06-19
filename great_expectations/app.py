import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from streamlit_extras.let_it_rain import rain
import pandas as pd
import time
import webbrowser
from great_expectations.geutils import DataQuality


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
        st.error('Test failed. View data docs for more details', icon="🚨")

    # Create data for the bar chart
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
        for item in partial_unexpected_list:
            st.write(item)
    else:
        st.write("No partial unexpected values found.")


def main():
    # Set the app title
    st.title("Data Quality APP")

    # Step 4: Implement the app components
    # Select the data source
    data_source = st.selectbox("Select the data source", ["", "california_housing_test.csv", "dataset1.csv", "dataset2.csv", "dataset3.csv"])

    DQ_APP = None  # Initialize DQ_APP object

    checks_input = None  # Initialize checks_input variable
    if data_source:
        # Display a preview of the data
        st.subheader("Preview of the data:")
        data = pd.read_csv(f"great_expectations/data/{data_source}")
        st.write(data.head())

        if DQ_APP is None:  # Create DQ_APP object if not already created
            DQ_APP = DataQuality(data_source, data)
        # Perform data quality checks
        st.subheader("Perform Data Quality Checks")

        checks_input = st.text_area("Describe the checks you want to perform")

        # Button to get started
        if checks_input:
            submit_button = st.button("Submit")
            if submit_button:
                with st.spinner('Running your data quality checks'):
                    time.sleep(5)
                    expectation_result = DQ_APP.run_expectation(checks_input)
                    #print(expectation_result.to_json_dict())
                    st.success('Your test has successfully been run! Get results')
                    with st.expander("Show Results"):
                        st.subheader("Data Quality result")
                        display_test_result(expectation_result.to_json_dict())

            open_docs_button = st.button("Open Data Docs")
            if open_docs_button:
                st.write("Open button clicked")
                #DQ_APP.get_data_docs()

                # Get the URL to the Data Docs
                data_docs_url = DQ_APP.context.get_docs_sites_urls()[0]['site_url']
                st.write(data_docs_url)

                # Open the URL in the browser
                webbrowser.open_new_tab(data_docs_url)

# Run the app
if __name__ == "__main__":
    main()
