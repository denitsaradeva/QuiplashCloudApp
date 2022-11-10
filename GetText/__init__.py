from itertools import tee
import json
import logging
import os
from re import S
import ssl

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import random


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Getting Text in progress....')
    # Create the needed proxy objects for CosmosDB account, database and prompt container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the prompts container
    prompts_container = db_client.get_container_client(os.environ['prompts_container'])

    user = req.get_json()

    word = user['word']
    logging.info(word)
    exact = user['exact']
    logging.info(exact)

    symbols = [",", ".", ":", ";", "!", "?"]
   
    try:
        result = []
        filtered = []
        prompts = list(prompts_container.query_items(query=("SELECT * FROM prompts"), enable_cross_partition_query=True))
        for prompt in prompts:
            prompt.pop('password')
            prompt.pop('_rid')
            prompt.pop('_self')
            prompt.pop('_etag')
            prompt.pop('_attachments')
            prompt.pop('_ts')
            content = json.dumps(prompt)
            newPrompt = json.loads(content)
            newPrompt["id"] = int(newPrompt["id"]) 
            filtered.append(newPrompt)
        if(len(prompts) > 0):
            for prompt in filtered:
                words = prompt.get('text').split()
                words[:] = [entry.replace(match, " ") if any((match := substring) in entry for substring in symbols) else entry for entry in words ]
                for entryWord in words:
                    comparisonWord = entryWord.split()
                    for comparison in comparisonWord:
                        if((exact and comparison == word) or ((not exact) and (comparison.lower()==word.lower()))):
                            result.append(prompt)
        
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": result}), status_code=200)

    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 