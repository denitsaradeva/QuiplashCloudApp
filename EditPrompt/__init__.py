from itertools import tee
import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Updating a Prompt in progress....')
    # Create the needed proxy objects for CosmosDB account, database, user, and prompt container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the prompts container
    prompts_container = db_client.get_container_client(os.environ['prompts_container'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(os.environ['users_container'])

    user = req.get_json()

    username = user['username']
    logging.info(username)
    password = user['password']
    logging.info(password)
    id = user['id']
    logging.info(id)
    text = user['text']
    logging.info(text)

    try:
        usersQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}' AND users.password = '{1}'".format(username, password)), enable_cross_partition_query=True))
        promptQuery = list(prompts_container.query_items(query=("SELECT * FROM prompts WHERE prompts.id = '{0}'".format(id)), enable_cross_partition_query=True))
        userPrompts = list(prompts_container.query_items(query=("SELECT prompts.text FROM prompts WHERE prompts.username = '{0}'".format(username)), enable_cross_partition_query=True))
        
        if(len(usersQuery) == 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "bad username or password" }), status_code=400)
        elif(len(promptQuery)==0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "prompt id does not exist" }), status_code=400)
        elif(len(text)<20 or len(text)>100):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "prompt length is <20 or >100 characters" }), status_code=400)
        logging.info("Prompts2")
        logging.info(userPrompts)
        for prompt in userPrompts:
            logging.info("GetText")
            logging.info(prompt.get('text'))
            logging.info("text")
            logging.info(text)
            if(prompt.get('text') == text):
                logging.info("error")
                return func.HttpResponse(body = json.dumps({"result": False, "msg": "This user already has a prompt with the same text" }), status_code=400)

        logging.info("Prompts")
        logging.info(userPrompts)
        content = json.dumps(promptQuery[0])
        newPrompt = json.loads(content)
        newPrompt["text"] = text

        prompts_container.upsert_item(newPrompt)
        
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 