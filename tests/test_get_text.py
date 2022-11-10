import logging
import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
from GetText import main
from unittest import TestCase

class TestFunction(unittest.TestCase):
    TestCase.maxDiff = None

    # note the config.settings to access configuration defined in config.py
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    # Create a proxy object to the quilplash Cosmos DB database
    db_client = client.get_database_client(config.settings['db_id'])

    # Create a proxy object to the users container
    users_container = db_client.get_container_client(config.settings['users_container'])

    def test_get_text(self):
        payload = {"word": "javascript", "exact" : True}

        resp = requests.get(
                'https://quiplash-dr5g20.azurewebsites.net/api/GetText?code=7g4N5YfA_Dct9qN7dfv-LQaGvI6Mo94k5m7XxVspQcdFAzFuahKajg==', 
                json = payload)

        self.assertEqual({'result': True, 'msg': [{'text': 'What app you would never code in JavaScript?', 'username': 'testest', 'id': 1}]}, resp.json())
# , {"text" : "What app you would never crash ever?", "username": "Deyan", "id": 8}, {"text" : "What app you would never program?", "username": "Maxim", "id": 9 }