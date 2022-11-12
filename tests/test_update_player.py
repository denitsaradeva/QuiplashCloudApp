import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
from UpdatePlayer import main

class TestFunction(unittest.TestCase):

    # note the config.settings to access configuration defined in config.py
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    # Create a proxy object to the quilplash Cosmos DB database
    db_client = client.get_database_client(config.settings['db_id'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(config.settings['users_container'])

    def test_update_user(self):
        payload = {"username": "Maxim" , "add_to_score": 40, "password": "deyandeyan"}

        resp = requests.get(
                'https://quiplash-dr5g20.azurewebsites.net/api/player/update?code=1BPLgOhBJITlT38I06ShEqKu6D3GA2k0JeFjMeRWiYCxAzFuENiFfg==', 
                json = payload)


        self.assertEqual({"result" : True, 'msg' : 'OK'}, resp.json())