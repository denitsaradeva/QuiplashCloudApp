import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
from EditPrompt import main

class TestFunction(unittest.TestCase):

    # note the config.settings to access configuration defined in config.py
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    # Create a proxy object to the quilplash Cosmos DB database
    db_client = client.get_database_client(config.settings['db_id'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(config.settings['users_container'])

    def test_edit_prompt(self):
        payload = {"id": 10, "text": "What app you would never use one two?", "username" : "Maxim" , "password": "deyandeyan"}

        resp = requests.get(
                'https://quiplash-dr5g20.azurewebsites.net/api/prompt/edit?code=8hSy74tMGCSh-X6vq2p_lPQDRZRLya_sr6sopDxigO9CAzFuaQDEKw==', 
                json = payload)


        self.assertEqual({"result" : True, 'msg' : 'OK'}, resp.json())