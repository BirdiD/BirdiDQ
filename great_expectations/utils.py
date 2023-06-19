import os

def get_mapping(folder_path):

    mapping_dict = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            name_without_extension = os.path.splitext(file_name)[0]
            name_with_uppercase = name_without_extension.capitalize()
            mapping_dict[name_with_uppercase] = file_name

    return mapping_dict
   
print(list(get_mapping('great_expectations/data/').keys()))