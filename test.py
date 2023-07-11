import great_expectations as ge
context = ge.get_context()

POSTGRES_CONNECTION_STRING='postgresql://postgres:FulaSpeechCorpora@localhost:5432/pulaar_translation_db'

pg_datasource = context.sources.add_or_update_sql(
    name="my_postgres_db", connection_string=POSTGRES_CONNECTION_STRING
)
print(pg_datasource)