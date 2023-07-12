import great_expectations as ge
import pandas as pd
import datetime
from great_expectations.checkpoint.checkpoint import SimpleCheckpoint
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

    
    def add_or_update_datasource_2(self):
        datasource = self.context.sources.add_or_update_pandas(name=self.datasource_name)
        return datasource
    
    def create_data_asset(self):
        datasource = self.add_or_update_datasource_2()
        asset_name = f"{self.datasource_name}_{self.partition_date.date()}"
        data_asset = datasource.add_dataframe_asset(name=asset_name, dataframe=self.dataframe)
        return data_asset
    
    def get_batch_resquest(self):
        asset_name = self.create_data_asset()
        batch_request = asset_name.build_batch_request()
        return batch_request
    
    def get_validator_2(self):
        """
        Retrieve a validator object for a fine grain adjustment on the expectation suite.
        """
        batch_request = self.get_batch_resquest()
        self.add_or_update_ge_suite()
        validator = self.context.get_validator(batch_request=batch_request,
                                               expectation_suite_name=self.expectation_suite_name,
                                        )
        return validator

    def add_checkpoint_2(self):
        batch_request = self.get_batch_resquest()
        checkpoint = SimpleCheckpoint(
            name=self.checkpoint_name,
            data_context=self.context,
            validations=[
                {
                    "batch_request": batch_request,
                    "expectation_suite_name": self.expectation_suite_name,
                },
            ],
        )
        self.context.add_or_update_checkpoint(checkpoint=checkpoint)
        return checkpoint
    
    def run_checkpoint(self, checkpoint):
        checkpoint_result = checkpoint.run()
        return checkpoint_result
    
    def run_checks(self, expectation):
        """
        Run your dataquality checks here
        """
        validator = self.get_validator_2()
        def my_function(expectation, validator):
            local_vars = {"validator": validator}
            exec(f"expectation_result = validator.{expectation}", globals(), local_vars)
            return local_vars.get("expectation_result")
        
        expectation_result = my_function(expectation, validator)


        validator.save_expectation_suite(discard_failed_expectations=False)
        checkpoint = self.add_checkpoint_2()
        self.run_checkpoint(checkpoint)
        return expectation_result
