import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
from RegisterPlayer import main

class TestFunction(unittest.TestCase):

    # note the config.settings to access configuration defined in config.py
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    # Create a proxy object to the treehuggers Cosmos DB database
    db_client = client.get_database_client(config.settings['db_id'])

    # Create a proxy object to the trees container
    users_container = db_client.get_container_client(config.settings['users_container'])

    def test_add_user(self):
        payload = {"username":  "testest" , "password" : "eeee1111"}


        resp = requests.get(
                'http://localhost:7071/api/RegisterPlayer', 
                json = payload)


        self.assertEqual({"result" : True, 'msg' : 'OK'}, resp.json())