import json, onos_connect

# config = {}


def generate_routes(config):
    intents_dict = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/intents"), config["username"], config["password"])
    routing_dict = {}

    # Build initial dict of routes
    for intent in range(len(intents_dict["intents"])): 
        key = intents_dict["intents"][intent]["key"]
        route = []
        route.append(key[:22])    
        for resource in range(len(intents_dict["intents"][intent]["resources"])):
            route.append(intents_dict["intents"][intent]["resources"][resource]["src"]["device"])
            route.append(intents_dict["intents"][intent]["resources"][resource]["dst"]["device"])
        route.append(key[22:])
        route = list(dict.fromkeys(route))
        routing_dict[key] = route
    return routing_dict


def generate_inents(routing_dict, config):
    imr_dict        = onos_connect.onos_get(onos_connect.url_builder(config["host"], config["port"], "/onos/v1/imr/imr/intentStats"), config["username"], config["password"])
    intents_dict    = {}
    intents_dict["routingList"] = []
    i = 0
    for path in routing_dict:
        rl_dict     = {}
        paths_dict  = {}
        paths_array = []
        paths       = []
        paths.append(routing_dict[path])
        paths_dict["path"]          = paths
        paths_dict["weight"]        = 1
        paths_array.append(paths_dict)
        rl_dict["paths"]            = paths_array
        rl_dict["key"]              = list(routing_dict.keys())[i]
        rl_dict["appId"]            = {}
        rl_dict["appId"]["id"]      = imr_dict["statistics"][0]["id"]
        rl_dict["appId"]["name"]    = "org.onosproject.ifwd"
        intents_dict["routingList"].append(rl_dict)
        i = i + 1
    return intents_dict




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
        