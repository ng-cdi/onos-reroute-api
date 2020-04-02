import base64
import json
import urllib.request, logging
from configs import *

logging.basicConfig(level=logging.INFO)

class OnosConnect:

    def __init__(self, api):
        self.__config = Configs().get_config()
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
