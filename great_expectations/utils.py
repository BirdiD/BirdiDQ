import os
from dotenv import load_dotenv
import openai
load_dotenv('.env')

def get_mapping(folder_path):

    mapping_dict = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            name_without_extension = os.path.splitext(file_name)[0]
            name_with_uppercase = name_without_extension.capitalize()
            mapping_dict[name_with_uppercase] = file_name

    return mapping_dict

def nltoge():
    """
    Convert Natural Lnaguage Query to GE expectation checks
    """
    ftmodel = "davinci:ft-personal-2023-06-22-11-04-40"

    prompt = "Can you check that the column username is not null for rows having 'FR' value in the countrycode column?\n\n###\n\n"
    response = openai.Completion.create(
    model=ftmodel,
    prompt=prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop= [" STOP"]
    )
    return response['choices'][0]['text']
