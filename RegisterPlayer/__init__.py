import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Inserting a User in progress....')

    # Create the needed proxy objects for CosmosDB account, database and user container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(os.environ['users_container'])

    user = req.get_json()

    username = user['username']
    password = user['password']
    user['id']=username
    user['games_played']=0
    user['total_score']=0

    try:
        creationQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}'".format(username)), enable_cross_partition_query=True))
        if(len(creationQuery) != 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Username already exists" }), status_code=400)
        elif(len(username) < 4 or len(username) > 16):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Username less than 4 characters or more than 16 characters"}), status_code=400)
        elif(len(password) < 8 or len(password) > 24):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Password less than 8 characters or more than 24 characters"}), status_code=400)

        users_container.create_item(body=user)
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)



    





 