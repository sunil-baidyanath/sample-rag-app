'''
Created on Jan 26, 2024

@author: sunilthakur
'''

'''
 System prompt controls personality and scope of the model
 
 Multiple function calling in sequence
 Token usage optimization
 Function calling with cognitive search [Using FC with RAG]
 Maintain session in data and read that using FC to be context aware.
 
 
 
'''

import os
import json

import openai
from openai import AzureOpenAI

AZURE_OPENAI_KEY = 'fb569c7a7f444edc82d434e58b525dd7'
AZURE_OPENAI_ENDPOINT = 'https://arogya-kys-ai.openai.azure.com/'

# openai.api_key = 'fb569c7a7f444edc82d434e58b525dd7'
# openai.api_base = 'https://arogya-kys-ai.openai.azure.com/' # your endpoint should look like the following https://YOUR_RESOURCE_NAME.openai.azure.com/
# openai.api_type = 'azure'
# openai.api_version = '2023-05-15' # this might change in the future
#
# deployment_name='gpt' #This will correspond to the custom name you chose for your deployment when you deployed a model. 
#
# # Send a completion call to generate an answer
# print('Sending a test completion job')
# start_phrase = 'Write a tagline for an ice cream shop. '
# response = openai.Completion.create(engine=deployment_name, prompt=start_phrase, max_tokens=10)
# # response = openai.chat.completions.create(engine=deployment_name, model='gpt-3.5-turbo', messages=start_phrase, max_tokens=10)
# text = response.choices[0]['text'].replace('\n', '').replace(' .', '.').strip()
# print(start_phrase+text)

def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})


client = AzureOpenAI(
  api_key = AZURE_OPENAI_KEY,  
  api_version = "2023-12-01-preview", #"2023-05-15",
  azure_endpoint = AZURE_OPENAI_ENDPOINT
)

messages = [{"role": "user", "content": "What's the weather like in San Francisco, Tokyo, and Paris?"}]
# functions = [{
#             "type": "function",
#             "function": {
#                 "name": "get_current_weather",
#                 "description": "Get the current weather in a given location",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "location": {
#                             "type": "string",
#                             "description": "The city and state, e.g. San Francisco, CA",
#                         },
#                         "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
#                     },
#                     "required": ["location"],
#                 },
#             },
#         }]

functions= [  
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"]
        }
    }
]  

# response = client.chat.completions.create(
#     model="gpt", # model = "deployment_name".
#     messages=[
#         {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
#         {"role": "user", "content": "Who were the founders of Microsoft?"}
#     ]
# )

response = client.chat.completions.create(
        model="gpt-functions",
        messages=messages,
        # tools=tools,
        # tool_choice="auto",  # auto is default, but we'll be explicit
        functions = functions,
        function_call="auto",
    )

print(messages)
response_message = response.choices[0].message
print(response_message)
print('\n')
# tool_calls = response_message.tool_calls
#
# # Step 2: check if the model wanted to call a function
# if tool_calls:
#         # Step 3: call the function
#         # Note: the JSON response may not always be valid; be sure to handle errors
#     available_functions = {
#         "get_current_weather": get_current_weather,
#     }  # only one function in this example, but you can have multiple
#     messages.append(response_message)  # extend conversation with assistant's reply
#         # Step 4: send the info for each function call and function response to the model
#     for tool_call in tool_calls:
#         function_name = tool_call.function.name
#         function_to_call = available_functions[function_name]
#         function_args = json.loads(tool_call.function.arguments)
#         function_response = function_to_call(
#             location=function_args.get("location"),
#             unit=function_args.get("unit"),
#         )
#
#         messages.append(
#         {
#             "tool_call_id": tool_call.id,
#             "role": "tool",
#             "name": function_name,
#             "content": function_response
#         })  # extend conversation with function response
#
#     second_response = client.chat.completions.create(
#         model="gpt",
#         messages=messages,
#     )  # get a new response from the model where it can see the function response
#
#     # return second_response
#
#     print(second_response.model_dump_json(indent=2))
# else:
#
#     print(response.choices[0].message.content)
    
if response_message.function_call:

    # Call the function. The JSON response may not always be valid so make sure to handle errors
    function_name = response_message.function_call.name

    available_functions = {
        "get_current_weather": get_current_weather,
    }
    
    function_to_call = available_functions[function_name] 

    function_args = json.loads(response_message.function_call.arguments)
    function_response = function_to_call(**function_args)

    # Add the assistant response and function response to the messages
    messages.append( # adding assistant response to messages
        {
            "role": response_message.role,
            "function_call": {
                "name": function_name,  
                "arguments": response_message.function_call.arguments,
            },
            "content": None
        }
    )
    messages.append( # adding function response to messages
        {
            "role": "function",
            "name": function_name,
            "content": function_response,
        }
    ) 

    # Call the API again to get the final response from the model
    second_response = client.chat.completions.create(
            messages=messages,
            model="gpt-functions"
            # optionally, you could provide functions in the second call as well
        )
    print(second_response)
    print(second_response.choices[0].message)
else:
    print(response)
    print(response.choices[0].message)