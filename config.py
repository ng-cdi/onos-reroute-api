import json

class config():

    def __init__(self, config_dict):
        self.__config_dict = load_config() 

    def load_json(filename):
        with open(filename) as f:
            return json.load(f)
    
    def load_config():
        try:
            return load_json("config.json")
        except:
            return load_json("config-default.json")
    
    def get_host():
        return config_dict["host"]

    def get_port():
        return config_dict["port"]

    def get_uname():
        return config_dict["username"]

    def get_passwd():
        return config_dict["password"]    



    