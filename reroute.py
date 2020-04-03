import json, traceback
import logging, random, sys

from onos_api import OnosAPI
from configs import Configs

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
                        return device

        return False
    
    # Does the host exist and is it connected to a list of devices
    def __is_host(self, host, devices):
        hosts = self.__onos.get_hosts()
        for device in devices:
            if self.__is_host_link(host, device, hosts):
                return device
        
        return False





    # def is_link(dev1, dev2, links_dict):
    #     for link in links_dict["links"]:
    #         if link["src"]["device"] == dev1 and link["dst"]["device"] == dev2:
    #             return True
    #     return False

    # Determine if the pushed intent is routable
    def __calc_src_host(self, key):
        return key[:22]

    def __calc_dst_host(self, key):
        return key[22:]

    def __is_key(self, key, new_intents):
        src_host = self.__calc_src_host(key)
        dst_host = self.__calc_dst_host(key)

        if new_intents[key][0] == src_host and new_intents[key][-1] == dst_host:
            return True

        return False

    # Example Syntax for __core_dev_calc
    # {
    #   "num_paths": 1,
    #   "core_dev": "of:000000000000000c",
    #    0: ["00:00:00:00:00:01/None", "of:0000000000000001", "of:0000000000000007", "of:000000000000000c", "00:00:00:00:00:07/None"]
    # }

    # {
    #   "num_paths": 2,
    #   "core_dev": "of:000000000000000c",
    #    0: ["00:00:00:00:00:01/None", "of:0000000000000001", "of:0000000000000007", "of:000000000000000c, "of:000000000000000d", "00:00:00:00:00:07/None"]
    #    1: ["00:00:00:00:00:01/None", "of:0000000000000001", "of:0000000000000007", "of:000000000000000c, "of:000000000000000e", "of:000000000000000d", "00:00:00:00:00:07/None"]
    # }

    # TODO: This is a bodge for a max of 3 core devices 
    # Needs to be fixed later. Infinate devs in core -- infinate loops. Needs good routing logic 
    # Assume it is NOT the dst_dev
    def __core_dev_calc(self, key, src_dev, metro_dev, dst_dev, core_dev, core_devs):

        calc_routes = {}
        calc_routes["num_paths"] = 0
        calc_routes["core_dev"] = core_dev

        # it is the dst dev
        if core_dev == dst_dev:
            calc_routes["num_paths"] = 1
            calc_list = []
            calc_list.append(self.__calc_src_host(key))
            calc_list.append(src_dev)
            calc_list.append(metro_dev)
            calc_list.append(dst_dev)
            calc_list.append(self.__calc_dst_host(key))
            calc_routes[0] = calc_list
            return calc_routes

        # 1 hop - only 3 devs, will calc...probably
        if self.__is_link(core_dev, dst_dev, self.__onos.get_links()):
            calc_routes["num_paths"] += 1
            calc_list = []
            calc_list.append(self.__calc_src_host(key))
            calc_list.append(src_dev)
            calc_list.append(metro_dev)
            calc_list.append(core_dev)
            calc_list.append(dst_dev)
            calc_list.append(self.__calc_dst_host(key))
            calc_routes[0] = calc_list

        # 2 hops - should calc
        core_devs.remove(core_dev)
        core_devs.remove(dst_dev)

        if self.__is_link(core_dev, core_devs[0], self.__onos.get_links()) and self.__is_link(core_devs[0], dst_dev, self.__onos.get_links()):
            calc_routes["num_paths"] += 1
            calc_list = []
            calc_list.append(self.__calc_src_host(key))
            calc_list.append(src_dev)
            calc_list.append(metro_dev)
            calc_list.append(core_dev)
            calc_list.append(core_devs[0])
            calc_list.append(dst_dev)
            calc_list.append(self.__calc_dst_host(key))
            calc_routes[1] = calc_list
        
        return calc_routes


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

    def generate_host_to_host_routes(self, key):
        layers = Configs("json/layers.json").get_config()

        # THIS ASSUMES THE HOSTS ARE NOT MULTI HOMED!! Will just get first in list

        src_dev = self.__is_host(self.__calc_src_host(key), layers.get("access"))
        dst_dev = self.__is_host(self.__calc_dst_host(key), layers.get("core"))

        # Check key exists and src is connected to access / dst is connected to core
        if not src_dev and dst_dev:
            return False
        
        # Get list of devs in metro src_dev has links to 
        metro_devs = []
        for device in layers.get("metro"):
            if self.__is_link(src_dev, device, self.__onos.get_links()):
                metro_devs.append(device)
        
        if len(metro_devs) == 0:
            return False
        
        # Dict of metro devs as keys mapped to array of core devs 


        # Dict Example
        # "of:0000000000000008":[
        #   {
        #       "num_paths": 1,
        #       "core_dev": "of:000000000000000c",
        #           0: ["00:00:00:00:00:01/None", "of:0000000000000001", "of:0000000000000007", "of:000000000000000c", "00:00:00:00:00:07/None"]
        #   },
        #   {
        #       "num_paths": 2,
        #       "core_dev": "of:000000000000000d",
        #           0: ["00:00:00:00:00:01/None", "of:0000000000000001", "of:0000000000000007", "of:000000000000000c, "of:000000000000000d", "00:00:00:00:00:07/None"]
        #           1: ["00:00:00:00:00:01/None", "of:0000000000000001", "of:0000000000000007", "of:000000000000000c, "of:000000000000000e", "of:000000000000000d", "00:00:00:00:00:07/None"]
        #   }
        # ]

        metro_core = {}
        for metro_dev in metro_devs:
            core_devs  = []
            for core_dev in layers.get("core"):
                # Calculate route through core - no assumptions core can be 1 to ∞
                if self.__is_link(metro_dev, core_dev, self.__onos.get_links()):
                    core_devs.append(self.__core_dev_calc(key, src_dev, metro_dev, dst_dev, core_dev, layers.get("core")))
            # Check it's managed to make a route - die if not
            if len(core_devs) == 0:
                return False
            metro_core[metro_dev] = core_devs
        
        # Dict example for export
        # "key" : "00:00:00:00:00:01/None00:00:00:00:00:07/None",
        # "num_routes" : 2
        # 0:[
        #     "00:00:00:00:00:01/None",
        #     "of:0000000000000001",
        #     "of:0000000000000007",
        #     "of:000000000000000c",
        #     "00:00:00:00:00:07/None"
        # ],
        # 1:[
        #     "00:00:00:00:00:01/None",
        #     "of:0000000000000001",
        #     "of:0000000000000007",
        #     "of:000000000000000c",
        #     "00:00:00:00:00:07/None"
        # ] etctectect....

        routes = {}
        routes["key"] = key
        routes["num_routes"] = "0"

        # def parse_routes(route_priority):
        #     for metro_dev in metro_devs:
        #         for core_route in metro_core[metro_dev]:
        #             if core_route["num_paths"] == 1:
        #                 routes[routes.get("num_routes")] = core_route.get(0)
        #                 routes["num_routes"] += 1

        # Tidy this up a bit later

        # Top Priority routes
        for metro_dev in metro_devs:
            for core_route in metro_core[metro_dev]:
                if core_route["num_paths"] == 1:
                    routes[routes.get("num_routes")] = core_route.get(0)
                    routes["num_routes"] = str(int(routes["num_routes"]) + 1)
        
        # Medium Priority Routes
        for metro_dev in metro_devs:
            for core_route in metro_core[metro_dev]:
                if core_route["num_paths"] == 2:
                    routes[routes.get("num_routes")] = core_route.get(0)
                    routes["num_routes"] = str(int(routes["num_routes"]) + 1)
        
        # Low Priority Routes
        for metro_dev in metro_devs:
            for core_route in metro_core[metro_dev]:
                if core_route["num_paths"] == 2:
                    routes[routes.get("num_routes")] = core_route.get(1)
                    routes["num_routes"] = str(int(routes["num_routes"]) + 1)

        return routes


        
