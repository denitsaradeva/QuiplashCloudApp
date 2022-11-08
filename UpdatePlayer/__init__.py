import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Updating a User in progress....')
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
    addToGamesPlayed = 0
    addToScore = 0
    try:
        addToGamesPlayed = user['add_to_games_played']
        if(addToGamesPlayed<=0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Value to add is <=0" }), status_code=400)
    except Exception as err:
        pass
    logging.info(addToGamesPlayed)
    try:
        addToScore = user['add_to_score']
        if(addToScore<=0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "Value to add is <=0" }), status_code=400)
    except Exception as err:
        pass
    logging.info(addToScore)

    try:
        usersQuery = list(users_container.query_items(query=("SELECT * FROM users WHERE users.username = '{0}'".format(username)), enable_cross_partition_query=True))
        passwordQuery = list(users_container.query_items(query=("SELECT users.password FROM users WHERE users.username = '{0}'".format(username)), enable_cross_partition_query=True))
        
        dbPassword = ""
        if(len(usersQuery)>0):
            dbPassword=passwordQuery[0].get('password')
        if(len(usersQuery) == 0):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "user does not exist" }), status_code=400)
        elif(password != dbPassword):
            return func.HttpResponse(body = json.dumps({"result": False, "msg": "wrong password" }), status_code=400)
        
        content = json.dumps(usersQuery[0])
        newUser = json.loads(content)
        newUser["games_played"] = newUser["games_played"] + addToGamesPlayed
        newUser["total_score"] = newUser["total_score"] + addToScore

        users_container.upsert_item(newUser)

        return func.HttpResponse(body = json.dumps({"result" : True, "msg": "OK" }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 