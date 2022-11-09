from itertools import tee
import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config
import random


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('Getting Prompts in progress....')
    # Create the needed proxy objects for CosmosDB account, database, user, and prompt container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the prompts container
    prompts_container = db_client.get_container_client(os.environ['prompts_container'])

    user = req.get_json()

    prompts = -1
    players = []
    try:
        prompts = user['prompts']
    except Exception:
        pass
    logging.info(prompts)
    try:
        players = user['players']
    except Exception:
        pass
    logging.info(players)

    try:
        if(len(players) != 0):
            result = []
            for player in players:
                prompts = list(prompts_container.query_items(query=("SELECT * FROM prompts WHERE prompts.username = '{0}'".format(player)), enable_cross_partition_query=True))
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
                    result.append(newPrompt)
            return func.HttpResponse(body = json.dumps({"result" : True, "msg": result }), status_code=200)
        elif(prompts != -1):
            result = []
            promptsQuery = list(prompts_container.query_items(query=("SELECT * FROM prompts"), enable_cross_partition_query=True))
            idQuery = list(prompts_container.query_items(query=("SELECT prompts.id FROM prompts"), enable_cross_partition_query=True))
            for prompt in promptsQuery:
                prompt.pop('password')
                prompt.pop('_rid')
                prompt.pop('_self')
                prompt.pop('_etag')
                prompt.pop('_attachments')
                prompt.pop('_ts')
                content = json.dumps(prompt)
                newPrompt = json.loads(content)
                newPrompt["id"] = int(newPrompt["id"]) 
                result.append(newPrompt)
            if (prompts > len(promptsQuery)):
                return func.HttpResponse(body = json.dumps({"result" : True, "msg": result }), status_code=200)
            else:
                randomResult = []
                idList = random.sample(idQuery, prompts)
                intIdList = []
                for id in idList:
                    content = json.dumps(id)
                    newPrompt = json.loads(content)
                    newPrompt["id"] = int(newPrompt["id"]) 
                    intIdList.append(newPrompt)
                for prompt in result:
                    if({"id" : prompt.get('id')} in intIdList):
                        randomResult.append(prompt)
                return func.HttpResponse(body = json.dumps({"result" : True, "msg": randomResult }), status_code=200)

    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 