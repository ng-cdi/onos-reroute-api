import json
import logging
from configs import *
import onos_connect

logging.basicConfig(level=logging.INFO)

class OnosAPI:

    def __init__(self):
        
    def load_json(self):
        self.__config = Configs().get_config()
        self.__devices = onos_connect.onos_get(onos_connect.url_builder(self.__config["host"], self.__config["port"], "/onos/v1/devices"), self.__config["username"], self.__config["password"])
        self.__hosts = onos_connect.onos_get(onos_connect.url_builder(self.__config["host"], self.__config["port"], "/onos/v1/hosts"), self.__config["username"], self.__config["password"])
        self.__links = onos_connect.onos_get(onos_connect.url_builder(self.__config["host"], self.__config["port"], "/onos/v1/links"), self.__config["username"], self.__config["password"])
        self.__intent_stats = onos_connect.onos_get(onos_connect.url_builder(self.__config["host"], self.__config["port"], "/onos/v1/imr/imr/intentStats"), self.__config["username"], self.__config["password"])
        self.__monitored_intents = onos_connect.onos_get(onos_connect.url_builder(self.__config["host"], self.__config["port"], "/onos/v1/imr/imr/monitoredIntents"), self.__config["username"], self.__config["password"])

    
    def get_devices(self):
        return self.__devices
    
    def get_hosts(self):
        return self.__hosts
    
    def get_links(self):
        return self.__links
    
    def get_intent_stats(self):
        return self.__intent_stats

    def get_monitored_intents(self):
        return self.__monitored_intents