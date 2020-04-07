import json
import logging

logging.basicConfig(level=logging.INFO)

class Configs:

    def __init__(self, config, default_config=None):
        self.__config = self.__load_config(config, default_config)

    def __load_json(self, filename):
        with open(filename) as f:
            return json.load(f)

    def __load_config(self, config, default_config=None):
        try:
            config = self.__load_json(config)
        except:
            logging.critical("Could not find configuration file: " + config)
            config = self.__load_json(default_config)
        return config

    def get_config(self):
        return self.__config
