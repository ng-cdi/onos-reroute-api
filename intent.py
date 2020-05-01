import json, base64
import coloredlogs, logging
import hashlib, copy, datetime, pytz
from flask_table import Table, Col
from reroute import Reroute
from hosts import Hosts
from onos_api import OnosConnect

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')

class Intent:

    def __init__(self, intent, api_key, users, spp_manager):
        self.__plaintext_intent   = intent.upper()
        self.__api_key  = api_key
        self.__users    = users
        self.__action   = ""
        self.__actors   = []
        self.__period   = []
        self.__spp_manager      = spp_manager
        self.__options_verb     = ""
        self.__options_subject  = ""
        self.__options_value    = ""
    
    # Test if we can proceed
    def __end_of_intent(self, current_element, intent_length, intent_arg):
        if current_element > intent_length:
            raise StopIteration('[Intent] Could not parse beyond ' + intent_arg)
    
    def parse(self):
        try:
            logger.info("[Intent] Starting to parse plaintext intent")
            intent_list = [x for x in self.__plaintext_intent.split(',')]
            logger.info("[Intent] Split Intent: [" + str(intent_list)[1:-1] + "]")
            intent_length = len(intent_list)
            logger.info("[Intent] Intent has " + str(intent_length) + " elements")
            current_element = 0
            
            self.__end_of_intent(current_element, intent_length, "start")
            
            # action
            self.__action = intent_list[current_element]
            current_element += 1
            self.__end_of_intent(current_element, intent_length, "action")
            logger.info("[Intent] Parsed Action: " + self.__action)

            # actors
            try:
                self.__actors = [x for x in intent_list[current_element].split(' ')]
            except:
                logger.error("[Intent] Could not split actors")
                raise
            
            current_element += 1
            self.__end_of_intent(current_element, intent_length, "actors")
            logger.info("[Intent] Parsed Actors: " + str(self.__actors)[1:-1])

            # period  
            try:
                self.__period = [x for x in intent_list[current_element].split(' ')]
            except:
                logger.error("[Intent] Could not split period")
                raise
            
            current_element += 1
            self.__end_of_intent(current_element, intent_length, "period")
            logger.info("[Intent] Parsed Period: " + str(self.__period)[1:-1])
              
        except StopIteration as err:
            logger.error(err.args)
            return err.args
        
        if self.__action == "CONNECT" and self.__period[0] == "UNLIMITED":
            logger.info("[Intent] Parsing CONNECT intent with best effort route")
            hosts = Hosts()
            src = hosts.get_host_id(self.__actors[0])
            dst = hosts.get_host_id(self.__actors[-1])
            reroute = Reroute()
            routes = reroute.generate_host_to_host_routes(src + dst)

            new_intents = {}
            new_intents[src + dst] = routes.get("routes").get("0")
            routing_dict = reroute.generate_routes()

            if (reroute.is_intent(routing_dict, new_intents)):
                if self.__spp_manager.is_spp(self.__users, self.__api_key):
                    logging.error("Could not modify Intents - Service Protection Period")
                    return "Could not modify Intents - Service Protection Period"
                else:
                    routing_dict.update(new_intents)
                    # logger.info(json.dumps(reroute.generate_intents(routing_dict), indent=4, sort_keys=True))
                    logger.info("[Intent]" + str(OnosConnect("/onos/v1/imr/imr/reRouteIntents").post(reroute.generate_intents(routing_dict))))
                    return False
                

            else:
                logging.error("Could not accept intent provided")
                return "Could accept the intent provided"

        elif self.__action == "PROTECT":
            logger.info("[Intent] Parsing PROTECT intent with best effort time eval")
            date = datetime.date.today().strftime("%Y/%m/%d")
            start = date + "T" + self.__period[1] + ":00+0000"
            end = date + "T" + self.__period[-1] + ":00+0000"
      
            logger.info("[Intent] Start Time: " + start)
            logger.info("[Intent] End Time: " + end)

            spp = {"priority": self.__users.get_level(self.__api_key), "enabled": True, "start_time": start, "end_time": end}
            spp_list = []
            spp_list.append(spp)
            self.__spp_manager.add_spp({"api_key": self.__api_key, "spp": spp_list}, self.__users)
            return False

        else:
            logger.info("[Intent] Could not parse the intent: " + self.__plaintext_intent)
            return "Could not parse the intent: " + self.__plaintext_intent


