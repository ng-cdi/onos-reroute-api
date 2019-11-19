import json
import onos_connect


def generate_routes(config):
    intents_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/intents"), config["username"], config["password"])
    routing_dict = {}

    # Build initial dict of routes
    for intent in range(len(intents_dict["intents"])):
        key = intents_dict["intents"][intent]["key"]
        route = []
        route.append(key[:22])
        for resource in range(len(intents_dict["intents"][intent]["resources"])):
            route.append(intents_dict["intents"][intent]
                         ["resources"][resource]["src"]["device"])
            route.append(intents_dict["intents"][intent]
                         ["resources"][resource]["dst"]["device"])
        route.append(key[22:])
        route = list(dict.fromkeys(route))
        routing_dict[key] = route
    return routing_dict


def generate_intents(routing_dict, config):
    imr_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/imr/imr/intentStats"), config["username"], config["password"])
    intents_dict = {}
    intents_dict["routingList"] = []
    i = 0
    for path in routing_dict:
        rl_dict = {}
        paths_dict = {}
        paths_array = []
        paths = []
        # paths.append(routing_dict[path])
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


def is_intent(routing_dict, new_intents, config):
    for key in list(dict.fromkeys(new_intents)):
        # Too short for an intent
        if len(new_intents[key] < 3):
            return False
        #  Does the key already exist?
        if key not in list(dict.fromkeys(routing_dict)):
            # Do the hosts exist?
            if host_exist(new_intents[key], config):
                # Is it a valid route?
                if is_route(new_intents[key], config):
                    return True
                else:
                    return False
            else:
                return False
        else:
            # Is it a valid route?
            if is_route(new_intents[key], config):
                return True
    return False


def host_exist(route, config):
    hosts_dict = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
    hosts_list = []
    for i in range(len(hosts_dict["hosts"])):
        hosts_list.append(hosts_dict["hosts"][i]["id"])
    
    if route[1] in hosts_list and route[-1] in hosts_list:
        return True
    
    return False

def devices_exist(route, devices_dict):
    devices_list = []
    for device in range(devices_dict["devices"]):
        devices_list.append(["id"])
    
    for device in range(route):
        if device not in devices_list:
            return False
    
    return True

def is_host_link(host, device, hosts_dict):
    for onos_host in range(hosts_dict["hosts"]):
        if onos_host["id"] == host:
            for locations in range(onos_host["locations"]):
                if locations["elementId"] == device:
                    return True

    return False

def is_link(dev1, dev2, links_dict):
    for link in links_dict["links"]:
        if link["src"]["device"] == dev1 and link["dst"]["device"] == dev2:
            return True
    return False

# Determine if the pushed intent is routable 
def is_route(route, config):
    hosts_dict      = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
    links_dict      = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/links"), config["username"], config["password"])
    devices_dict    = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/devices"), config["username"], config["password"])

    # check host connections 
    if not is_host_link(route[1], route[2], hosts_dict) or not is_host_link(route[-1], route[-2], hosts_dict):
        return False
    # remove hosts
    del route[1]
    del route[-1]
    # Only one device, must be true - passed the hosts conn test
    if len(route) < 2:
        return True
    
    # Check devices exist 
    if not devices_exist(route, devices_dict):
        return False
    
    dst_dev = route[-1]

    for i in range(len(route)):
        # Made it to the destination device
        if route[i] == dst_dev:
            return True
        
        # Is there a link to the next device?
        if not is_link(route[i], route[i + 1], links_dict):
            return False
    
    return False
        
        

# def is_link(links_dict, src_sw, dst_sw):
#     for link in len(range(links_dict["links"])):
#         if links_dict["link"][link]["src"]["device"] == src_sw and links_dict["link"][link]["dst"]["device"] == dst_sw:
#             return True
#     return False


# def find_host_switch(route, hosts_dict, host):
#     for rroute in range(len(hosts_dict["hosts"])):
#         if hosts_dict["host"][rroute]["id"] == host:
#             return hosts_dict["host"][rroute]["locations"][0]["elementId"]


# def sort_routes(route, key, hosts_dict, links_dict, intent_dict):
#     src_host = route[1]
#     dst_host = route[-1]
#     src_sw = find_host_switch(route, hosts_dict, src_host)
#     dst_sw = find_host_switch(route, hosts_dict, dst_host)

#     # If only 1 switch, return list as is
#     if src_sw == dst_sw:
#         return route

#     # If only 2 switches, order and return
#     if len(route) < 5 and isLink(links_dict, src_sw, dst_sw):
#         route[2] = src_sw
#         route[-2] = dst_sw
#         return route

#     # 3 or more switches...
#     switches = route
#     # remove hosts from array
#     del switches[1]
#     del switches[-1]


#     while(True):


# def generate_routes(config):
#     # global config = config
#     intents_dict    = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/imr/imr/intentStats"), config["username"], config["password"])
#     hosts_dict      = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
#     links_dict      = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/links"), config["username"], config["password"])
#     intent_dict     = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/intents"), config["username"], config["password"])

#     routing_list = {}
#     keys = []

#     # Build initial dict of routes
#     for intent in range(len(intents_dict["statistics"][0]["intents"])):
#         key = list(intents_dict["statistics"][0]["intents"][intent].keys())[0]
#         keys.append(key)
#         route = []
#         route.append(intents_dict["statistics"][0]["intents"][intent][key][0]["selector"]["criteria"][2]["mac"] + "/None")
#         for rroute in range(len(intents_dict["statistics"][0]["intents"][intent][key])):
#             route.append(intents_dict["statistics"][0]["intents"][intent][key][rroute]["deviceId"])
#         route.append(intents_dict["statistics"][0]["intents"][intent][key][len(intents_dict["statistics"][0]["intents"][intent][key]) - 1]["selector"]["criteria"][1]["mac"] + "/None")
#         routing_list[key] = route

#     #Sort routes

#     for k in keys:
#         sort_routes(routing_list[k], k, hosts_dict, links_dict, intent_dict)


#     print(route[1])
