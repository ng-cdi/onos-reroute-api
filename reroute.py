import json, traceback
import logging, random, sys

from onos_api import OnosAPI

logging.basicConfig(level=logging.INFO)

    # A routing dict entry looks like this:
    # "00:00:00:00:00:02/None00:00:00:00:00:04/None":[
    #         "00:00:00:00:00:02/None",
    #         "of:0000000000000001",
    #         "of:0000000000000002",
    #         "00:00:00:00:00:04/None"
    #     ],

class Reroute:
    def __init__(self):
        self.__onos = OnosAPI()


    def __is_link(self, dev1, dev2, links_dict):
        for link in links_dict["links"]:
            if link["src"]["device"] == dev1 and link["dst"]["device"] == dev2:
                return True
        return False

    def __calculate_path(self, devices, links_dict, src_sw, dst_sw):
        current_devices = []
        shuffle_devices = devices.copy()
        random.shuffle(shuffle_devices)
        if self.__is_link(src_sw, shuffle_devices[0], links_dict):
            current_devices.append(shuffle_devices[0])
            while True:
                if self.__is_link(shuffle_devices[0], shuffle_devices[1], links_dict):
                    shuffle_devices.remove(shuffle_devices[0])
                    current_devices.append(shuffle_devices[0])
                else:
                    return self.__calculate_path(devices, links_dict, src_sw, dst_sw)
                if len(shuffle_devices) == 1 and self.__is_link(shuffle_devices[0], dst_sw, links_dict):
                    current_devices.append(shuffle_devices[0])
                    current_devices.append(dst_sw)
                    return current_devices
        else:
            return self.__calculate_path(devices, links_dict, src_sw, dst_sw)

    

    def __host_exist(self, route):
        hosts_dict = self.__onos.get_hosts()
        hosts_list = []
        for onos_host in hosts_dict.get("hosts"):
            hosts_list.append(onos_host["id"])

        if route[1] in hosts_list and route[-1] in hosts_list:
            return True

        return False


    def __devices_exist(self, route, devices_dict):
        devices_list = []
        for device in devices_dict["devices"]:
            devices_list.append(device["id"])

        for device in route:
            if device not in devices_list:
                logging.warning(device + ": Device not found")
                return False

        return True


    def __is_host_link(self, host, device, hosts_dict):
        for onos_host in hosts_dict.get("hosts"):
            if onos_host["id"] == host:
                for locations in onos_host["locations"]:
                    if locations["elementId"] == device:
                        return True

        return False


    # def is_link(dev1, dev2, links_dict):
    #     for link in links_dict["links"]:
    #         if link["src"]["device"] == dev1 and link["dst"]["device"] == dev2:
    #             return True
    #     return False

    # Determine if the pushed intent is routable


    def __is_key(self, key, new_intents):
        src_host = key[:22]
        dst_host = key[22:]

        if new_intents[key][0] == src_host and new_intents[key][-1] == dst_host:
            return True

        return False


    def __is_route(self,route, key):
        hosts_dict = self.__onos.get_hosts()
        links_dict = self.__onos.get_links()
        devices_dict = self.__onos.get_devices()

        # check host connections
        if not self.__is_host_link(route[0], route[1], hosts_dict):
            logging.warning(
                key + ": There is no link between the src host and src device")
            return False

        if not self.__is_host_link(route[-1], route[-2], hosts_dict):
            logging.warning(
                key + ": There is no link between the dst host and dst device")
            return False

        # remove hosts
        link_list = route.copy()
        del link_list[0]
        del link_list[-1]
        # Only one device, must be true - passed the hosts conn test
        if len(link_list) < 2:
            logging.info(key + ": Single-hop link exists")
            return True

        # Check devices exist
        if not self.__devices_exist(link_list, devices_dict):
            logging.warning(key + ": Device not found")  
            return False

        dst_dev = link_list[-1]

        for i in range(len(link_list)):
            # Made it to the destination device
            if link_list[i] == dst_dev:
                logging.info(key + ": Multi-hop link exists")
                return True

            # Is there a link to the next device?
            if not self.__is_link(link_list[i], link_list[i + 1], links_dict):
                logging.warning(key + ": No link between device " +
                                link_list[i] + " and device " + link_list[i + 1])
                return False

        return False


    #################################################
    # Public Methods 
    #################################################

    def is_intent(self, routing_dict, new_intents):
        for key in list(dict.fromkeys(new_intents)):
            # Too short for an intent
            if len(new_intents[key]) < 3:
                logging.warning(key + " is too short for an intent")
                return False
            if not self.__is_key(key, new_intents):
                logging.warning(key + " does not match the hosts provided: " +
                                new_intents[key][0] + " and " + new_intents[key][-1])
                return False
            #  Does the key already exist?
            if key not in list(dict.fromkeys(routing_dict)):
                # Do the hosts exist?
                logging.info(
                    key + " does not already exist in current intents list")
                if self.__host_exist(new_intents[key]):
                    # Is it a valid route?
                    if self.__is_route(new_intents[key], key):
                        return True
                    else:
                        return False
                else:
                    logging.warning(key + " hosts do not exist on onos")
                    return False
            else:
                # Is it a valid route?
                logging.info(key + " exists in current intents list")
                if self.__is_route(new_intents[key], key):
                    return True
        return False

    def generate_routes(self):
        hosts_dict            = self.__onos.get_hosts()
        links_dict            = self.__onos.get_links()
        # devices_dict          = self.__onos.get_devices()
        intentStats_dict      = self.__onos.get_intent_stats()
        monitoredIntents_dict = self.__onos.get_monitored_intents()

        routing_dict = {}

        intents_dict = intentStats_dict["statistics"][0]["intents"]
        monitored_dict = monitoredIntents_dict["response"][0]["intents"]

        for monitored_intent in monitored_dict:
            logging.info("Processing intent: " + monitored_intent["key"])
            for intent in intents_dict:
                if intent.get(monitored_intent["key"], "") != "":
                    key = monitored_intent.get("key")
                    route = []
                    route.append(monitored_intent["inElements"][0])
                    # one hop intents
                    if len(intent[monitored_intent["key"]]) == 1:
                        route.append(intent[monitored_intent["key"]][0]["deviceId"])
                    
                    # multi hop intents
                    # elif len(intent[monitored_intent["key"]]) > 1:
                    else:
                        src_sw = ""
                        dst_sw = ""
                        devices = []
                        for i in range(len(intent[key])):
                            for onos_host in hosts_dict.get("hosts"):
                                if onos_host["id"] == monitored_intent["inElements"][0] and len(onos_host["locations"][0]["elementId"]) > 2:
                                    src_sw = onos_host["locations"][0]["elementId"]
                                elif onos_host["id"] == monitored_intent["outElements"][0] and len(onos_host["locations"][0]["elementId"]) > 2:
                                    dst_sw = onos_host["locations"][0]["elementId"]
                            devices.append(intent[key][i]["deviceId"])
                        
                        # Remove local and remote switches - see what's left
                        try:
                            devices.remove(src_sw)
                            devices.remove(dst_sw)
                        except:
                            logging.warning("Could not remove " + src_sw + " or " + dst_sw + "from path  for " + key + ". Route will not be valid!")
                            # traceback.print_exc(file=sys.stdout)
                        try:
                            # 2 Hops
                            if len(devices) == 0:
                                route.append(src_sw)
                                route.append(dst_sw)
                            
                            # 3 Hops
                            elif len(devices) == 1:
                                route.append(src_sw)
                                route.append(devices[0])
                                route.append(dst_sw)
                            
                            # 4 + Hops
                            elif len(devices) > 1:
                                route.append(src_sw)
                                route = route + self.__calculate_path(devices, links_dict, src_sw, dst_sw)
                            
                            else:
                                logging.warning("Could not calculate a route for " + key)
                        except:
                            logging.warning("Could not calculate a route for " + key)
                            # traceback.print_exc(file=sys.stdout)
                            

                    route.append(monitored_intent["outElements"][0])     
                    route = list(dict.fromkeys(route))
                    routing_dict[key] = route
        
        return routing_dict           



                # if intent == monitored_intent["key"]:
                #     print(intent)
        # break
        # # Build initial dict of routes
        # for intent in range(len(intents_dict["intents"])):
        #     key = intents_dict["intents"][intent]["key"]
        #     route = []
        #     route.append(key[:22])
        #     # 1 hop intents
        #     if len(intents_dict["intents"][intent]["resources"]) == 0:
        #         for onos_host in hosts_dict["hosts"]:
        #             # Some hosts aren't listed in /v1/hosts.. try the reverse too
        #             if onos_host["id"] == key[:22] or onos_host["id"] == key[22:]:
        #                 if len(onos_host["locations"][0]["elementId"]) > 2:
        #                     route.append(onos_host["locations"][0]["elementId"])
        #                     break
        #     # Multi-hop intents
        #     else:
        #         for resource in range(len(intents_dict["intents"][intent]["resources"])):
        #             route.append(intents_dict["intents"][intent]["resources"][resource]["src"]["device"])
        #             route.append(intents_dict["intents"][intent]["resources"][resource]["dst"]["device"])
        #     route.append(key[22:])
        #     route = list(dict.fromkeys(route))
        #     routing_dict[key] = route
        # return routing_dict






    def generate_intents(self, routing_dict):
        imr_dict = self.__onos.get_intent_stats()
        intents_dict = {}
        intents_dict["routingList"] = []
        i = 0
        for path in routing_dict:
            rl_dict = {}
            paths_dict = {}
            paths_array = []
            paths_dict["path"] = routing_dict[path]
            paths_dict["weight"] = 1
            paths_array.append(paths_dict)
            rl_dict["paths"] = paths_array
            rl_dict["key"] = list(routing_dict.keys())[i]
            rl_dict["appId"] = {}
            rl_dict["appId"]["id"] = imr_dict["statistics"][0]["id"]
            rl_dict["appId"]["name"] = "org.onosproject.ifwd"
            intents_dict["routingList"].append(rl_dict)
            i = i + 1
        return intents_dict



    def generate_host_to_host_intents(self, key):
        return


        
