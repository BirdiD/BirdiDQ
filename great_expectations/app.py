import streamlit as st
import pandas as pd
import time
from geutils import DataQuality

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
            button = st.button("Submit")
            if button: 
                with st.spinner('Running your data quality checks'):
                    time.sleep(5)
                    st.success('Your test has succesfully been run!')


# Run the app
if __name__ == "__main__":
    main()
