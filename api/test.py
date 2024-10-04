'''
Created on Jul 11, 2024

@author: sunilthakur
'''
import json

from app.api.chatbot.core.pipelines import IndexPipeline, QueryPipeline



with open('/Users/sunilthakur/eclipse-workspace/arogya-app/app/api/chatbot/conf/default.json') as fp:
    config = json.load(fp)

# build_knowledge_pipeline = IndexPipeline(config)
# index = build_knowledge_pipeline.run()

query = ''
user_query_pipeline = QueryPipeline(config)

while not query.lower() in ['quit', 'exit', 'end']:
    print('\nAsk your question \n')

    query = str(input())

    if not query.lower() in ['quit', 'exit', 'end']:

        result = user_query_pipeline.run(query)
        print(result)

        # update_context_pipeline = Pipeline()
        # update_context_pipeline.run()

    else:
        print('Ending your session')