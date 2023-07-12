import great_expectations as ge
from ruamel import yaml
import ruamel
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
from great_expectations.checkpoint.checkpoint import SimpleCheckpoint
from dotenv import load_dotenv, find_dotenv
import os 
import psycopg2
from sqlalchemy import create_engine
import pandas as pd 

load_dotenv(find_dotenv())

# Get your postgresql connection string from the environment variable
POSTGRES_CONNECTION_STRING = os.environ.get('POSTGRES_CONNECTION_STRING')

def read_pg_tables(table_name):
    """
    Read postgresql table in pandas dataframe
    """
    engine = create_engine(POSTGRES_CONNECTION_STRING)
    df = pd.read_sql_query(f'select * from {table_name}',con=engine)
    return df

def get_pg_tables():
    """
    List all tables from a PostgreSQL database using a connection string
    """
    conn = psycopg2.connect(POSTGRES_CONNECTION_STRING)
    cursor = conn.cursor()

    query = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
    cursor.execute(query)

    tables = cursor.fetchall()
    tables = [t[0] for t in tables]
    cursor.close()
    conn.close()
    return tables

def postgresql_data_owners():
    """
    Map each postgresql with its data owner
    """
    tables = get_pg_tables()
    return {datasource : 'postgreso@birdidq.com' for datasource in tables}

class PostgreSQLDatasource():
    """
    Run Data Quality checks on PostgreSQL data database
    """
    def __init__(self, database, asset_name):
        """ 
        Init class attributes
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
        datasource_yaml = rf"""
        name: {self.asset_name}
        class_name: Datasource
        execution_engine:
            class_name: SqlAlchemyExecutionEngine
            connection_string: {POSTGRES_CONNECTION_STRING}
        data_connectors:
            default_runtime_data_connector_name:
                class_name: RuntimeDataConnector
                batch_identifiers:
                    - default_identifier_name
            default_inferred_data_connector_name:
                class_name: InferredAssetSqlDataConnector
                include_schema_name: true
        """
        self.context.test_yaml_config(datasource_yaml)
        self.context.add_datasource(**yaml.load(datasource_yaml, Loader=ruamel.yaml.Loader))

    def configure_datasource(self):
        """
        Add a RuntimeDataConnector
        """
        batch_request = RuntimeBatchRequest(
            datasource_name=self.database,
            data_connector_name="default_runtime_data_connector_name",
            data_asset_name=self.asset_name,  # this can be anything that identifies this data
            runtime_parameters={"query": f"SELECT * from public.{self.asset_name} LIMIT 10"},
            batch_identifiers={"default_identifier_name": "default_identifier"},
        )
        # batch_request = BatchRequest(
        #     datasource_name=self.database,
        #     data_connector_name="default_inferred_data_connector_name",
        #     data_asset_name=f"public.{self.asset_name}", 
        # )
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


