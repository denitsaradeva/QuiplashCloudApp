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

    # Create the needed proxy objects for CosmosDB account, database and tree container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the treehuggers Cosmos DB database
    # Read reference here: https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.databaseproxy?view=azure-python
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the trees container
    # Read reference here: https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.containerproxy?view=azure-python
    users_container = db_client.get_container_client(config.settings['users_container'])


    user = req.get_json()
    username = user['username']
    logging.info(username)
    password = user['password']
    logging.info(password)
    user['id']=username
    logging.info(user)

    # Insert code here to translate from the request with 'tree_id' : int to a JSON with 
    # 'id' :string so you can insert into trees_container


    # Read the documentation of the create_item method and tree
    # https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.containerproxy?view=azure-python#azure-cosmos-containerproxy-create-item
    # Reference on Python exception handling: https://docs.python.org/3.9/tutorial/errors.html

    try:
        logging.info("before creation")
        creationQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}'".format(username)), enable_cross_partition_query=True))
        if(len(creationQuery) != 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Username already exists" }), status_code=400)
        elif(len(username) < 4 or len(username) > 16):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Username less than 4 characters or more than 16 characters"}), status_code=400)
        elif(len(password) < 8 or len(password) > 24):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Password less than 8 characters or more than 24 characters"}), status_code=400)
        # the right create_item call
        # If everything went well return the right response according to specification
        users_container.create_item(body=user)
        logging.info("user created successfully")
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         #Return the right response according to specification when something goes wrong
         # Does this exception matches what we need in the specifications
         logging.info("throws cosmos response error")
         logging.info(e.message)
         pass
    return func.HttpResponse("", status_code=200)


    # An alternative to the try-except approach is to query for the item before inserting



    





 