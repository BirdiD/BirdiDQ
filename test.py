import great_expectations as ge
from ruamel import yaml
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
from great_expectations.checkpoint.checkpoint import SimpleCheckpoint
from dotenv import load_dotenv, find_dotenv
import os 
import psycopg2

load_dotenv(find_dotenv)

# Get your postgresql connection string from the environment variable
#POSTGRES_CONNECTION_STRING = os.environ.get('POSTGRES_CONNECTION_STRING')


def get_pg_tables():
    """
    List all tables from a PostgreSQL database using a connection string
    """
    # Connect to the PostgreSQL database
    conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Query to retrieve all table names
    query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
    # Execute the query
    cursor.execute(query)

    # Fetch all the table names
    tables = cursor.fetchall()
    tables = [t[0] for t in tables]
    # Close the cursor and connection
    cursor.close()
    conn.close()
    return tables

class PostgreSQLDatasource():
    def __init__(self, database, asset_name):
        """ 
        create great expectations context and default runtime datasource
        """
        self.database = database
        self.asset_name = asset_name
        self.expectation_suite_name = f"{asset_name}_expectation_suite"
        self.checkpoint_name = f"{asset_name}_checkpoint"
        self.context = ge.get_context()

    def add_or_update_datasource(self):
        """
        Create data source if it does not exist or updating existing one
        """
        datasource_config = {
            "name": f"{self.database}",
            "class_name": "Datasource",
            "execution_engine": {
                "class_name": "SqlAlchemyExecutionEngine",
                "connection_string": f"{POSTGRES_CONNECTION_STRING}",
            },
            "data_connectors": {
                "default_runtime_data_connector_name": {
                    "class_name": "RuntimeDataConnector",
                    "batch_identifiers": ["default_identifier_name"],
                },
                "default_inferred_data_connector_name": {
                    "class_name": "InferredAssetSqlDataConnector",
                    "include_schema_name": True,
                },
            },
        }
        self.context.test_yaml_config(yaml.dump(datasource_config))
        self.context.add_datasource(**datasource_config)

    def configure_datasource(self):
        """
        Add a RuntimeDataConnector
        """
        batch_request = BatchRequest(
            datasource_name=self.database,
            data_connector_name="default_inferred_data_connector_name",
            data_asset_name=f"public.{self.asset_name}", 
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
        self.add_or_update_datasource()
        batch_request = self.configure_datasource()
        self.add_or_update_ge_suite()
        validator = self.context.get_validator(batch_request=batch_request,
                                               expectation_suite_name=self.expectation_suite_name,
                                        )
        return validator, batch_request

    def run_expectation(self, expectation):
        """
        Run your dataquality checks here
        """
        validator, batch_request = self.get_validator()
        def my_function(expectation, validator):
            local_vars = {"validator": validator}
            exec(f"expectation_result = validator.{expectation}", globals(), local_vars)
            return local_vars.get("expectation_result")
        
        expectation_result = my_function(expectation, validator)
        exec(f"expectation_result = validator.{expectation}")

        validator.save_expectation_suite(discard_failed_expectations=False)
        self.run_ge_checkpoint(batch_request)
        return expectation_result
    
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

    def run_ge_checkpoint(self, batch_request):
        """
        Run GE checkpoint
        """
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

dabatabase = "pulaar_translation_db"
asset_name = "users"
#dq = PostgreSQLDatasource(dabatabase, asset_name)
# result = dq.run_expectation("expect_column_values_to_not_be_null(column='email')")
# print(result)

print(os.environ)