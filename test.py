import great_expectations as ge
from ruamel import yaml
from great_expectations.core.batch import BatchRequest, RuntimeBatchRequest
context = ge.get_context()

POSTGRES_CONNECTION_STRING='postgresql://postgres:FulaSpeechCorpora@localhost:5432/pulaar_translation_db'
 
datasource_config = {
    "name": "my_postgres_datasource",
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

context.test_yaml_config(yaml.dump(datasource_config))
context.add_datasource(**datasource_config)

# Here is a BatchRequest naming a table
batch_request = BatchRequest(
    datasource_name="my_postgres_datasource",
    data_connector_name="default_inferred_data_connector_name",
    data_asset_name="public.classifications",  # this is the name of the table you want to retrieve
)
context.add_or_update_expectation_suite(expectation_suite_name="test_suite")
validator = context.get_validator(
    batch_request=batch_request, expectation_suite_name="test_suite"
)
print(validator.head())