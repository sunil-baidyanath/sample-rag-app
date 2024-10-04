'''
Created on Mar 8, 2024

@author: sunilthakur
'''
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.core import Settings
from llama_index.core import SQLDatabase
from llama_index.core.indices.struct_store.sql_query import NLSQLTableQueryEngine

# Connect to the database
username = 'root'
password = quote_plus('Baidyanath@205')

engine = create_engine("mysql+mysqlconnector://"+username+":"+password+"@localhost/test")

# Test the connection
# connection = engine.connect()
#
# result = connection.execute(text("SELECT * FROM student"))
#
# for row in result:
#     print(row)
#
# table_details = {
#     "student": "stores student’s data."
#     }

llm = AzureOpenAI(
    deployment_name="gpt-functions",
    model="gpt-3.5-turbo", 
    api_key="fb569c7a7f444edc82d434e58b525dd7",
    azure_endpoint="https://arogya-kys-ai.openai.azure.com/",
    api_version="2023-12-01-preview", temperature=0.0
)

Settings.llm = llm
Settings.embed_model = 'local'
# Settings.callback_manager = CallbackManager([token_counter])

tables = ["student"]
# sql_database = SQLDatabase(engine, include_tables=tables,sample_rows_in_table_info=5)
sql_database = SQLDatabase(engine, sample_rows_in_table_info=2)#by default3 (actually)
print(sql_database.get_usable_table_names())

# Settings.llm = llm

query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database
)


query_str = "which student is the oldest?"
# query_str ="What are the most frequently mentioned keywords or phrases in the comments made by sales representatives"
response = query_engine.query(query_str)
print(response)