import json, base64
import logging, coloredlogs
import urllib.request, logging
from configs import Configs


coloredlogs.install(level='INFO')


class OnosAPI:

    def __init__(self):
        self.__devices = {}
        self.__hosts = {}
        self.__links = {}
        self.__intent_stats = {}
        self.__monitored_intents = {}
        self.load_json()
        
    def load_json(self):
        self.__devices = OnosConnect("/onos/v1/devices").get()
        self.__hosts = OnosConnect("/onos/v1/hosts").get()
        self.__links = OnosConnect("/onos/v1/links").get()
        self.__intent_stats = OnosConnect("/onos/v1/imr/imr/intentStats").get()
        self.__monitored_intents = OnosConnect("/onos/v1/imr/imr/monitoredIntents").get()

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

class OnosConnect:

    def __init__(self, api):
        self.__config = Configs("json/config.json", "config-default.json").get_config()
        self.__url = self.url_builder(api)
        
    def auth_http(self):
        request = urllib.request.Request(self.__url)
        base64string = base64.encodestring(
            ('%s:%s' % (self.__config.get("username"), self.__config.get("password"))).encode()).decode().replace('\n', '')
        request.add_header('Authorization', 'Basic %s' % base64string)
        return request

    def get(self):
        request = self.auth_http()
        response = urllib.request.urlopen(request)
        return json.loads(response.read())

    def post(self, json_data):
        request = self.auth_http()
        request.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(request, data=bytes(json.dumps(json_data), encoding="utf-8"))
        return json.loads(response.read())

    def url_builder(self, api):
        url = "http://" + self.__config.get("host") + ":" + self.__config.get("port") + api
        logging.info("Parsed url: " + url)
        return url
