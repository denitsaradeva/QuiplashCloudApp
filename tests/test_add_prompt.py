import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
from CreatePrompt import main

class TestFunction(unittest.TestCase):

    # note the config.settings to access configuration defined in config.py
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    # Create a proxy object to the quilplash Cosmos DB database
    db_client = client.get_database_client(config.settings['db_id'])

    # Create a proxy object to the prompts container
    prompts_container = db_client.get_container_client(config.settings['prompts_container'])

    def test_add_prompt(self):
        payload = {"text": "What app you would never get up in the middle of the night?", "username": "Deyan" , "password": "deyandeyan"}

        resp = requests.get(
                'https://quiplash-dr5g20.azurewebsites.net/api/prompt/create?code=zN1tIzEh0EP_JvpkJ2j-xP807eb1_XJQekp4_0PgjULUAzFuHOmYSw==', 
                json = payload)


        self.assertEqual({"result" : True, 'msg' : 'OK'}, resp.json())