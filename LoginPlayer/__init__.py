import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Logging in a User in progress....')
    # Create the needed proxy objects for CosmosDB account, database and user container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(os.environ['users_container'])


    user = req.get_json()
    username = user['username']
    logging.info(username)
    password = user['password']
    logging.info(password)

    try:
        usernameQuery = list(users_container.query_items(query=("SELECT users.username FROM users WHERE users.username = '{0}'".format(username)), enable_cross_partition_query=True))
        passwordQuery = list(users_container.query_items(query=("SELECT users.password FROM users WHERE users.username = '{0}'".format(username)), enable_cross_partition_query=True))
        dbUsername=usernameQuery[0].get('username')
        dbPassword=passwordQuery[0].get('password')

        if(password == dbPassword and username == dbUsername):
            return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
        else:
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Username or password incorrect" }), status_code=400)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 