import json
import logging
import os
from re import S

import azure.functions as func
import azure.cosmos as cosmos
import azure.cosmos.exceptions as exceptions
import config


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Creating leaderboard in progress....')
    # Create the needed proxy objects for CosmosDB account, database and user container
    client = cosmos.cosmos_client.CosmosClient(os.environ['db_URI'], os.environ['db_key'] )

    # Create a proxy object to the quiplashcw Cosmos DB database
    db_client = client.get_database_client(os.environ['db_id'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(os.environ['users_container'])

    leaderboardInfo = req.get_json()

    count = leaderboardInfo['top']

    try:
        leaderboard = []
        usersQuery = list(users_container.query_items(query=("SELECT * FROM users ORDER BY users.total_score DESC, users.username ASC"), enable_cross_partition_query=True))

        for i in range(count):
            currentUser = {"username": usersQuery[i].get("username") , "score": usersQuery[i].get("total_score"), "games_played": usersQuery[i].get("games_played")}
            leaderboard.append(currentUser)
        return func.HttpResponse(body = json.dumps({"result" : True, "msg": leaderboard }), status_code=200)
    except exceptions.CosmosHttpResponseError as e:
         logging.info("throws cosmos response error")
         logging.info(e.message)
         return func.HttpResponse("", status_code=200)


    





 