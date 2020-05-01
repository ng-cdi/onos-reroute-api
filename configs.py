import json
import logging, coloredlogs

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

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
            logger.critical("Could not find configuration file: " + config)
            config = self.__load_json(default_config)
        return config

    def get_config(self):
        return self.__config
