import logging, datetime, json, traceback, sys
from spp import SPP

logging.basicConfig(level=logging.INFO)

class SppManager:

    def __init__(self):
        self.__service_protection_periods = []
    
    def get_spp_total(self):
        return len(self.__service_protection_periods)
    
    def get_spp_active(self):
        active_spp = 0

        for spp in self.__service_protection_periods:
            if spp.is_spp():
                active_spp += 1
        
        return active_spp

    def get_spp_unactive(self):
        unactive_spp = 0

        for spp in self.__service_protection_periods:
            if not spp.is_spp():
                unactive_spp += 1
        
        return unactive_spp
    
    def is_spp(self):
        for spp in self.__service_protection_periods:
            if spp.is_spp():
                return True
        
        return False
    
    def add_spp(self, spp_dict, users):
    
        for spp_json in spp_dict.get("spp"):
            # if spp_json.get("priority"):
            spp = SPP()
            load_errs = spp.load_spp(spp_json, username)
            if not load_errs:
                return load_errs

            self.__service_protection_periods.append(spp)
        return ""

    def __add_spp(self, spp_dict):
        spp = SPP()
        spp.load_spp(spp_dict)
        self.__service_protection_periods.append(spp)
        return ""
    
    def remove_spp(self):
        return "todo"
    
    def export(self):
        exports = []
        for spp in self.__service_protection_periods:
            export_json = {}
            export_json["username"] = spp.get_username
            export_json["enabled"] = spp.get_enabled
            export_json["priority"] = spp.get_priority
            export_json["start_time"] = spp.get_start_time().isoformat()
            export_json["end_time"] = spp.get_end_time().isoformat()
            exports.append(export_json)

        return {"spp":exports}
    
    def save(self):
        try:
            with open('json/spp.json', 'w') as path:
                json.dump(self.export(), path, sort_keys=True, indent=4)
        except:
            logging.warning("Couldn't save SPP json. Continuing...")
            traceback.print_exc(file=sys.stdout)
    
    def __load(self):
        try:
            with open('data.json', 'r') as path:
                imports = json.load(path)

            for spp in imports.get("spp"):
                self.__add_spp(spp)
        except:
            logging.warning("Couldn't load SPP json. Continuing...")
            traceback.print_exc(file=sys.stdout)


        
            

