import logging, datetime, json, traceback, sys
from spp import SPP

logging.basicConfig(level=logging.INFO)

class SppManager:

    def __init__(self):
        self.__service_protection_periods = []
        self.__load()
    
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
    
    def add_spp(self, spp_dict, users=None):

        if users == None:
            for spp_json in spp_dict.get("spp"):
                spp = SPP()
                load_errs = spp.load_spp(spp_json)
                if load_errs:
                    return load_errs
                self.__service_protection_periods.append(spp)
        
        else:
            for spp_json in spp_dict.get("spp"):
                spp = SPP()
                print(users.get_user(spp_dict.get("api_key")))
                load_errs = spp.load_spp(spp_json, users.get_user(spp_dict.get("api_key")))
                if load_errs:
                    return load_errs
                if spp_json.get("priority") >= users.get_level(spp_dict.get("api_key")):
                    self.__service_protection_periods.append(spp)
                else:
                    return "User [" + users.get_user(spp_dict.get("api_key")) + "] level [" + users.get_level(spp_dict.get("api_key")) + "] is not authorised to create an SPP for that Priority Level [" + spp_json.get("priority") + "]"
        
        self.save()
        return ""
    
    def remove_spp(self):
        return "todo"
    
    def export(self):
        exports = []
        for spp in self.__service_protection_periods:
            export_json = {}
            export_json["username"] = spp.get_username()
            export_json["enabled"] = spp.get_enabled()
            export_json["priority"] = spp.get_priority()
            export_json["start_time"] = spp.get_start_time().isoformat()
            export_json["end_time"] = spp.get_end_time().isoformat()
            export_json["uuid"] = spp.get_uuid()
            exports.append(export_json)

        spp_export = {}
        spp_export["spp"]  = exports

        return spp_export
    
    def save(self):
        try:
            with open('json/spp.json', 'w') as path:
                json.dump(self.export(), path, sort_keys=True, indent=4)
        except:
            logging.warning("Couldn't save SPP json. Continuing...")
            traceback.print_exc(file=sys.stdout)
    
    def __load(self):
        try:
            with open('json/spp.json', 'r') as path:
                imports = json.load(path)
    
            errs = self.add_spp(imports)
            if errs:
                logging.warning(errs)
        except:
            logging.warning("Couldn't load SPP json. Continuing...")
            traceback.print_exc(file=sys.stdout)


        
            

