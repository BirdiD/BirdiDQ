# About 🔍

BirdiDQ is an intuitive and user-friendly data quality application that allows you to run data quality checks on top of python great expectation open source library using natural language queries. Type in your requests, and BirdiDQ will generate the appropriate GE method, run the quality control and return the results along with data docs you need. 

## Features

- **Natural Language Processing**: Understands your text queries and converts them into GE methods .
- **Instant Results**: Run data quality checks on selected table.
- **GEN AI models**: Uses finetuned LLM on customed expectations data.

## Queries example

Here are some example queries you can try with SnowChat:

- Ensure that at least 80% of the values in the country column are not null.
- Is the median value in the temperature column between 18 and 25 degrees?
- Check that none of the values in the address column match the pattern for an address starting with a digit.
