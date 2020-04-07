import json
import logging
import datetime
import dateutil.parser

logging.basicConfig(level=logging.INFO)

class SPP:

    def __init__(self):
        self.__enabled = False
        self.__start_time = datetime.datetime.now()
        self.__end_time = datetime.datetime.now()
        self.__username = ""
        self.__priority = 10

    def load_spp(self, spp_dict, username=None):
        if username is None:
            self.__username = spp_dict.get("username")
            self.__enabled = spp_dict.get("enabled")
            self.__start_time = dateutil.parser.parse(spp_dict.get("start_time"))
            self.__end_time = dateutil.parser.parse(spp_dict.get("end_time"))
            self.__priority = spp_dict.get("priority")
            return ""
        else:
            self.__username = username
            try:
                if isinstance(spp_dict.get("enabled"), bool):
                    self.__enabled = spp_dict.get("enabled")
                else:
                    raise Exception()
            except:
                return "Could not parse enabled variable. Check the type (bool)."
            
            try:
                if isinstance(spp_dict.get("priority"), int):
                    self.__priority = spp_dict.get("priority")
                else:
                    raise Exception()
            except:
                return "Could not parse priority variable. Check the type (int)."
            
            try:
                if isinstance(spp_dict.get("start_time"), str):
                    self.__start_time = dateutil.parser.parse(spp_dict.get("start_time"))
                else:
                    raise Exception()
            except:
                return "Could not parse start_date variable. Check it is in ISO 8601 format (str)"

            try:
                if isinstance(spp_dict.get("end_time"), str):
                    self.__end_time = dateutil.parser.parse(spp_dict.get("end_time"))
                else:
                    raise Exception()
            except:
                return "Could not parse end_date variable. Check it is in ISO 8601 format (str)"
            
            return ""

    def __is_spp_time(self):
        now = datetime.datetime.now()
        if self.__start_time < now and self.__end_time > now:
            return True
        return False

    def is_spp(self):
        if self.__enabled and self.__is_spp_time():
            return True
        return False

    def enable(self):
        self.__enabled = True
    
    def disable(self):
        self.__enabled = False
    
    def get_enabled(self):
        return self.__enabled

    def get_start_time(self):
        return self.__start_time
    
    def get_end_time(self):
        return self.__end_time
