import json, base64
import logging
import hashlib, copy
from flask_table import Table, Col


logging.basicConfig(level=logging.INFO)

class Users:

    def __init__(self):
        self.__users = self.__load_users("json/users.json")
        self.__generate_hash_keys()

    def __load_json(self, filename):
        with open(filename) as f:
            return json.load(f)

    def __load_users(self, config):
        try:
            config = self.__load_json(config)
        except:
            logging.critical("Could not find configuration file: " + config)
        return config
    
    def __generate_hash_keys(self):
        for user in self.__users.get("users"):
            hashed = hashlib.sha256(user.get("api_key").encode())
            user["hashed_api_key"] = hashed.hexdigest()

    def get_key(self, username):
        for user in self.__users.get("users"):
            if user.get("username") == username:
                return user.get("api_key")  
        return ""
    
    def get_user(self, key):
        for user in self.__users.get("users"):
            if user.get("api_key") == key:
                return user.get("username")  
        return ""
    
    def get_hashed_key(self, username):
        for user in self.__users.get("users"):
            if user.get("username") == username:
                return user.get("hashed_api_key")
        return ""
    
    def authenticate(self, key):
        for user in self.__users.get("users"):
            if user.get("api_key") == key:
                return True
        return False
    
    def get_level(self, key):
        # Try to match api_key
        for user in self.__users.get("users"):
            if user.get("api_key") == key:
                return user.get("level")
        # Try to match username (fallback - is safe as already authed) --- no it's not
        # for user in self.__users.get("users"):
        #     if user.get("username") == key:
        #         return user.get("level")
        return 0
    
    def get_users(self):
        users = copy.deepcopy(self.__users)
        for user in users.get("users"):
            del user["api_key"]
        return users
    
    def get_user_table(self):        
        items = []
        for user in self.get_users().get("users"):
            items.append(Item(user.get("username"), user.get("level"), user.get("hashed_api_key")))
        table = ItemTable(items)
        
        return table.__html__()



# Declare your table
class ItemTable(Table):
    classes = ['table table-dark']
    name = Col('Username')
    level = Col('Level')
    hashed_pass = Col('Hashed_Pass')

# Get some objects
class Item(object):
    def __init__(self, name, level, hashed_pass):
        self.name = name
        self.level = level
        self.hashed_pass = hashed_pass

