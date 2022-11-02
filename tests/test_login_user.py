import unittest
import json
import requests 

import azure.functions as func
import azure.cosmos as cosmos
import config
#Important for the import name to match the case of the Function folder
from LoginPlayer import main

class TestFunction(unittest.TestCase):

    # note the config.settings to access configuration defined in config.py
    client = cosmos.cosmos_client.CosmosClient(config.settings['db_URI'], config.settings['db_key'] )

    # Create a proxy object to the treehuggers Cosmos DB database
    db_client = client.get_database_client(config.settings['db_id'])

    # Create a proxy object to the trees container
    users_container = db_client.get_container_client(config.settings['users_container'])

    def test_login_user(self):
        payload = {"username":  "ggg2" , "password" : "eeee1111"}


        resp = requests.get(
                'https://quiplash-dr5g20.azurewebsites.net/api/LoginPlayer?code=NIgbXsedB16kw07mT6hBaQnWmV58lM3SEE2D6dwTA6CcAzFuQ0wIsQ==', 
                json = payload)


        self.assertEqual({"result" : True, 'msg' : 'OK'}, resp.json())