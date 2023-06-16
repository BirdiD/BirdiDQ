import great_expectations as ge
import pandas as pd
import datetime
import base64
from great_expectations.core.batch import RuntimeBatchRequest
from great_expectations.checkpoint.checkpoint import SimpleCheckpoint
import os
from ruamel import yaml
import ruamel
import IPython
import streamlit as st
import streamlit.components.v1 as components

class DataQuality():

    def __init__(self, datasource_name, dataframe):
        """ 
        create great expectations context and default runtime datasource
        """
        self.datasource_name = datasource_name
        self.expectation_suite_name = f"{datasource_name}_expectation_suite"
        self.checkpoint_name = f"{datasource_name}_checkpoint"
        self.dataframe = dataframe
        self.partition_date = datetime.datetime.now()
        self.context = ge.get_context()

    def add_or_update_datasource(self):
        """
        Create data source if it does not exist or updating existing one
        """
        datasource_yaml = rf"""
        name: {self.datasource_name}
        class_name: Datasource
        execution_engine:
            class_name: PandasExecutionEngine
        data_connectors:
            runtime_connector:
                class_name: RuntimeDataConnector
                batch_identifiers:
                    - run_id
        """
        self.context.test_yaml_config(datasource_yaml)
        self.context.add_datasource(**yaml.load(datasource_yaml, Loader=ruamel.yaml.Loader))
    
    def configure_datasource(self):
        """
        Add a RuntimeDataConnector hat uses an in-memory DataFrame to a Datasource configuration
        """
        batch_request = RuntimeBatchRequest(
            datasource_name= self.datasource_name,
            data_connector_name= "runtime_connector",
            data_asset_name=f"{self.datasource_name}_{self.partition_date.strftime('%Y%m%d')}",
            batch_identifiers={
                "run_id": f'''
                {self.datasource_name}_partition_date={self.partition_date.strftime('%Y%m%d')}
                ''',
            },
            runtime_parameters={"batch_data": self.dataframe}
        )
        return batch_request
    
    def add_or_update_ge_suite(self):
        """
        create expectation suite if not exist and update it if there is already a suite
        """
        self.context.add_or_update_expectation_suite(
                     expectation_suite_name = self.expectation_suite_name)

    def get_validator(self):
        """
        Retrieve a validator object for a fine grain adjustment on the expectation suite.
        """
        batch_request = self.configure_datasource()
        self.add_or_update_ge_suite()
        validator = self.context.get_validator(batch_request=batch_request,
                                               expectation_suite_name=self.expectation_suite_name,
                                        )
        return validator
    
    def run_expectation(self, expectation):
        """
        Run your dataquality checks here
        """
        validator = self.get_validator()

        exec(f"expectation_result = validator.{expectation}")

        validator.save_expectation_suite(discard_failed_expectations=False)
        self.run_ge_checkpoint()
    
    def add_or_update_ge_checkpoint(self):
        """
        Create new GE checkpoint or update an existing one
        """
        checkpoint_config = {
                    "name": self.checkpoint_name,
                    "class_name": "SimpleCheckpoint",
                    "run_name_template": "%Y%m%d-%H%M%S",
                }
        self.context.test_yaml_config(yaml.dump(checkpoint_config))
        self.context.add_or_update_checkpoint(**checkpoint_config)

    def run_ge_checkpoint(self):
        """
        Run GE checkpoint
        """
        batch_request = self.configure_datasource()
        self.add_or_update_ge_checkpoint()

        self.context.run_checkpoint(
                checkpoint_name = self.checkpoint_name,
                validations=[
                            {
                             "batch_request": batch_request,
                            "expectation_suite_name": self.expectation_suite_name,
                            }
                            ],
                )
    def open_data_docs(self):
        """
        Define the button to open the HTML file
        """
        if st.button('Open Data Docs'):
            # Generate Data Docs
            self.context.open_data_docs()

            # Get the URL to the Data Docs
            data_docs_url = self.context.get_docs_sites_urls()[0]['site_url']

            # Display the link to the Data Docs
            st.markdown(f"Click [here]({data_docs_url}) to open the Data Docs.")

datasource_name = "birdi"
df = pd.read_csv("great_expectations/data/california_housing_test.csv")
DQ_APP = DataQuality(datasource_name, df)
check = "expect_column_values_to_not_be_null(column='total_rooms', mostly=0.8, condition_parser='pandas', row_condition='population<=800')"
DQ_APP.run_expectation(check)

#create expectation suite if not exist
# expectation_suite_name = "birdi_suite"
# context.add_or_update_expectation_suite(
#                 expectation_suite_name = expectation_suite_name
#             )

#pass that request into context.get_validator
# validator = context.get_validator(
#     batch_request=batch_request,
#     expectation_suite_name=expectation_suite_name,
# )

#Save validation
# expectation = validator.expect_column_values_to_not_be_null(column="total_rooms", mostly=0.70)
# validator.save_expectation_suite(discard_failed_expectations=False)


#Add checkpoint

# checkpoint_config = {
#                 "name": checkpoint_name,
#                 "class_name": "SimpleCheckpoint",
#                 "run_name_template": "%Y%m%d-%H%M%S",
#             }
# context.test_yaml_config(yaml.dump(checkpoint_config))
# context.add_or_update_checkpoint(**checkpoint_config)
#context.add_or_update_checkpoint(checkpoint=checkpoint)
#print(checkpoint)

#Run checkpoint
# checkpoint_result = context.run_checkpoint(
#             checkpoint_name = checkpoint_name,
#             validations=[
#                 {
#                     "batch_request": batch_request,
#                     "expectation_suite_name": expectation_suite_name,
#                 }
#             ],
#         )

#context.build_data_docs()

# get the latest running data documentation
# data_docs_path = f'great_expectations/uncommitted/data_docs/local_site/validations/{expectation_suite_name}'
# latest_file = max(os.listdir(data_docs_path))
# render_path = os.path.join(data_docs_path, latest_file)

# print(f"Render path is {render_path}")


# for k,v in checkpoint_result['run_results'].items():
#     render_file = v['actions_results']['update_data_docs']['local_site'].replace('file://', '')

# print(f"Render file is {render_file}")

# Define the title
st.title('Data Quality')

# Get user input for data quality check
data_quality_check = st.text_input('Enter the data quality check you want to perform', value='Example sentence placeholder')


DQ_APP.open_data_docs()
