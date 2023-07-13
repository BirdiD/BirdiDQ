# About 🔍

BirdiDQ is an intuitive and user-friendly data quality application that allows you to run data quality checks on top of python great expectation open source library using natural language queries. Type in your requests, and BirdiDQ will generate the appropriate GE method, run the quality control and return the results along with data docs you need.

## Features

- **Data Exploration**: Quickly and interactively explore your data (apply filters, comparison, etc.)
- **Natural Language Processing**: Understands your text queries and converts them into GE methods.
- **Instant Results**: Run data quality checks on selected datasource.
- **Automate Email Alert**: Alert Data Owners when you find inconsistencies in the data
- **GEN AI models**: Uses finetuned LLM on customed expectations data.

## Tech Stack

This app is an LLM-powered app built using:

- **[Streamlit](https://streamlit.io/)**
- **[Great Expectations](https://github.com/Soulter/hugging-chat-api)**
- **Finetuned LLMs**:
  - **[Falcon-7B parameters causal decoder-only model](https://huggingface.co/tiiuae/falcon-7b)**: The model is finetuned on custom data with **Qlora** approach.
  - **[OpenAI GPT-3](https://platform.openai.com/docs/guides/fine-tuning)**: Also finetuned on the same data
- **Note**: The finetuned GPT-3 model seems to perform better for now.

## Queries example

Here are some example queries you can try with BirdiDQ:

- Ensure that at least 80% of the values in the country column are not null.
- Check that none of the values in the address column match the pattern for an address starting with a digit.
