import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
from streamlit_extras.let_it_rain import rain


def display_test_result(result):
    # Define CSS styles for the success and failure boxes
    success_style = "border-radius: 5px; padding: 10px; background-color: #C8E6C9; color: #388E3C;"
    failure_style = "border-radius: 5px; padding: 10px; background-color: #FFCDD2; color: #D32F2F;"

    # Check if the test was successful
    success = result.get("Success", False)

    # Display the test result box
    if success:
        st.success('This is a success message!', icon="✅")
        rain(emoji="🎈",
             font_size=54,
             falling_speed=5,
             animation_length="infinite",
            )
    else:
        st.error('Test failed. View data docs for more details', icon="🚨")

    # Create data for the bar chart
    labels = ['Element Count', 'Unexpected Count', 'Unexpected Percent']
    values = [report['Element Count'], report['Unexpected Count'], report['Unexpected Percent']]
    colors = ['lightskyblue', 'lightcoral', 'lightgreen']

    # Create a bar chart using Plotly
    fig = go.Figure(data=go.Bar(x=labels, y=values, marker=dict(color=colors)))
    fig.update_layout(title='Data Quality Test Results', xaxis_title='Metrics', yaxis_title='Values')

    # Display the bar chart using Streamlit's Plotly support
    st.plotly_chart(fig)

    # Display other details of the report
    st.subheader("Expectation Type")
    st.write(report["Expectation Type"])

    st.subheader("Partial Unexpected List")
    partial_unexpected_list = report["Partial Unexpected List"]
    if partial_unexpected_list:
        for item in partial_unexpected_list:
            st.write(item)
    else:
        st.write("No partial unexpected values found.")

report = {
    "Success": False,
    "Expectation Type": "expect_column_values_to_not_be_null",
    "Element Count": 305,
    "Unexpected Count": 0,
    "Unexpected Percent": 0.0,
    "Partial Unexpected List": [],
    "Expectation Configuration": {
        "column": "total_rooms",
        "condition_parser": "pandas",
        "row_condition": "population<=500",
        "batch_id": "california_housing_test.csv-california_housing_test.csv_2023-06-19"
    }
}
display_test_result(report)