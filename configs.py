import json

class Configs:

    def __init__(self):
        self.__config = self.load_config("config.json", "config-default.json")
        self.__layers = self.load_config("layers.json")

    def load_json(self, filename):
        with open(filename) as f:
            return json.load(f)

    def load_config(self, config, default_config=None):
        try:
            config = load_json(config)
        except:
            config = load_json(default_config)
        return config

    def get_config(self):
        return self.__config
    
    def get_layers(self):
        return self.__layers