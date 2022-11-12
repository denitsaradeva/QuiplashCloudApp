from cmath import log
import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Inserting a Prompt in progress....')

    # Create the needed proxy objects for CosmosDB account, database, user, and prompt container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the prompts container
    prompts_container = db_client.get_container_client(os.environ['prompts_container'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(os.environ['users_container'])

    prompt = req.get_json()

    username = prompt['username']
    password = prompt['password']
    text = prompt['text']

    try:
        checkQuery = list(prompts_container.query_items(query=("SELECT prompts.text FROM prompts"), enable_cross_partition_query=True))
        creationQuery = list(prompts_container.query_items(query=("SELECT prompts.text FROM prompts WHERE prompts.username = '{0}'".format(username)), enable_cross_partition_query=True))
        userQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}' AND users.password = '{1}'".format(username, password)), enable_cross_partition_query=True))
        texts = [entry.get('text') for entry in creationQuery]
        if(len(checkQuery) == 0):
            newId = 1
        else:
            idQuery=list(prompts_container.query_items(query=("SELECT VALUE MAX (StringToNumber(prompts.id)) from prompts"), enable_cross_partition_query=True))
            newId = idQuery[0]+1
            logging.info(newId)
        prompt['id']=str(newId)
        if(len(userQuery) == 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "bad username or password" }), status_code=400)
        elif(text in texts):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "This user already has a prompt with the same text" }), status_code=400)
        elif(len(text) < 20 or len(text) > 100):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "prompt length is <20 or > 100 characters" }), status_code=400)

        prompts_container.create_item(body=prompt)
        logging.info("user created successfully")
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)






 