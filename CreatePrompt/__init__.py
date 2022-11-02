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
    logging.info('Inserting a User in progress....')

    # Create the needed proxy objects for CosmosDB account, database, user, and prompt container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    # Read reference here: https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.databaseproxy?view=azure-python
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the prompts container
    # Read reference here: https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.containerproxy?view=azure-python
    prompts_container = db_client.get_container_client(os.environ['prompts_container'])

    # Create a proxy object to the users container
    # Read reference here: https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.containerproxy?view=azure-python
    users_container = db_client.get_container_client(os.environ['users_container'])


    prompt = req.get_json()
    username = prompt['username']
    logging.info(username)
    password = prompt['password']
    text = prompt['text']
    logging.info(password)
    logging.info(prompt)
    logging.info(text)

    # Insert code here to translate from the request with 'tree_id' : int to a JSON with 
    # 'id' :string so you can insert into trees_container


    # Read the documentation of the create_item method and tree
    # https://learn.microsoft.com/en-us/python/api/azure-cosmos/azure.cosmos.containerproxy?view=azure-python#azure-cosmos-containerproxy-create-item
    # Reference on Python exception handling: https://docs.python.org/3.9/tutorial/errors.html

    try:
        creationQuery = list(prompts_container.query_items(query=("SELECT prompts.text FROM prompts WHERE prompts.username = '{0}'".format(username)), enable_cross_partition_query=True))
        userQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}' AND users.password = '{1}'".format(username, password)), enable_cross_partition_query=True))
        idQuery=list(prompts_container.query_items(query=("SELECT * FROM prompts ORDER BY prompts.id DESC"), enable_cross_partition_query=True))

        newId = (int)(idQuery[0].get('id'))+1
        texts = [entry.get('text') for entry in creationQuery]
        prompt['id']=str(newId)
        if(len(userQuery) == 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "bad username or password" }), status_code=400)
        elif(text in texts):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "This user already has a prompt with the same text" }), status_code=400)
        elif(len(text) < 20 or len(text) > 100):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "prompt length is <20 or > 100 characters" }), status_code=400)

        # the right create_item call
        # If everything went well return the right response according to specification
        prompts_container.create_item(body=prompt)
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



    





 