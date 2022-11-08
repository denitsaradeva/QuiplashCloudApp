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
    logging.info('Deleting a Prompt in progress....')
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

    try:
        usersQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}' AND users.password = '{1}'".format(username, password)), enable_cross_partition_query=True))
        promptQuery = list(prompts_container.query_items(query=("SELECT * FROM prompts WHERE prompts.id = '{0}'".format(id)), enable_cross_partition_query=True))
    
        targetUsername = None
        if(len(promptQuery)>0):
            targetUsername = promptQuery[0].get('username')
        if(len(usersQuery) == 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "bad username or password" }), status_code=400)
        elif(len(promptQuery)==0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "prompt id does not exist" }), status_code=400)
        if(targetUsername != username):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "access denied" }), status_code=400)
        
        prompts_container.delete_item(str(id), str(id))
        
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 