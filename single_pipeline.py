# from main import *
# Import necessary libraries
import json
import requests
import time
from dotenv import load_dotenv
load_dotenv()
import os

# Get the Groq API key
GROQ_API_KEY = os.getenv("GROQ_API")
MODEL="gemma2-9b-it"
# Global variable to keep track of the total number of tokens
total_tokens = 0
def call_groq_api(api_key, model, messages, temperature=0.0, max_tokens=7000, n=1):
    print(messages)
    """
    NOTE: DO NOT CHANGE/REMOVE THE TOKEN COUNT CALCULATION 
    Call the Groq API to get a response from the language model.
    :param api_key: API key for authentication
    :param model: Model name to use
    :param messages: List of message dictionaries
    :param temperature: Temperature for the model
    :param max_tokens: Maximum number of tokens to generate (these are max new tokens)
    :param n: Number of responses to generate
    :return: Response from the API
    """
    global total_tokens
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    
    # model = "llama-3.3-70b-versatile"
    # messages = [
    #     {
    #         "role": "user",
    #         "content": "Explain the importance of fast language models"
    #     }
    # ]
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    data = {
        "model": model,
        "messages": messages,
        'temperature': temperature,
        'max_tokens': max_tokens,
        'n': n
    }

    response = requests.post(url, headers=headers, json=data)
    response_json = response.json()
    print(response_json)


    # Update the global token count
    total_tokens += response_json.get('usage', {}).get('completion_tokens', 0)
    completion_text = response_json["choices"][0]["message"]["content"]

    # You can get the completion from response_json['choices'][0]['message']['content']
    # return response_json, total_tokens
    return completion_text, total_tokens


# raw prompt
def table_agent(query):
    # table_schema=get_table_schema()
    database_schema=get_database_schema(query)
    messages = [
        {
            "role": "user",

            "content": f"User want solution for for given query {query} and the schema for the database tables is {database_schema} it is organised in priority wise as per vetcor similarity. Just return all the tables we need to responsd to given user query just return list of that tables. Return it in string format table name separated by ',' comma and amke sure table name is same as in table schema"
        }
    ]
    response,tokens=call_groq_api(GROQ_API_KEY ,MODEL,messages)
    
    return response
def prune_agent(query):
    response_tab_agent=table_agent(query)
    required_table_details=""
    required_tables=response_tab_agent.split(",")

    for table in required_tables:
        table_schema=get_table_schema(table)
        messages = [
            {
                "role": "user",
                
                "content": f"You are an expert in Intent understanding and SQL schema As per user query{query} filter all the attributes or columns i need in the given table{table_schema}. This is needed details only for given table with respect tot his given query no other tables and otehr thing. return it in json object format. like one key required true or false is tabel required and other things if required thne all the attriutes or column name i need to respond this query"
            }
        ]
        table_attributes_required,t=call_groq_api(GROQ_API_KEY,MODEL,messages)
        required_table_details+=table_attributes_required
    return required_table_details

def final_sql_query_generator(query):
    required_table_details=prune_agent(query)
    sql_statement=""
    messages = [
            {
                "role": "user",
                
                "content": f"You are an expert in Intent understanding and SQL schema  As per user query{query} and below table_schema{required_table_details}. Generate a sql query which can provide resposne to this user query and provide right response. I want only sql query nothing else not extra words or anything"
            }
        ]
    sql_statement=call_groq_api(GROQ_API_KEY,MODEL,messages)
    return sql_statement






# sample only
def get_database_schema(query):
    """
    Fetches the relevant database schema for a given query.
    :return: JSON string of database schema.
    """
    return json.dumps({
        "tables": [
            {"name": "employees", "columns": ["id", "name", "salary", "department_id"]},
            {"name": "departments", "columns": ["id", "name"]}
        ]
    })

# Mock function to get schema of a specific table
def get_table_schema(table_name):
    """
    Fetches the schema of a specific table.
    :return: JSON string of table schema.
    """
    schemas = {
        "employees": {"id": "int", "name": "varchar", "salary": "float", "department_id": "int"},
        "departments": {"id": "int", "name": "varchar"}
    }
    return json.dumps(schemas.get(table_name, {}))
final_sql_query_generator("For finding salary of highest paid employee")
