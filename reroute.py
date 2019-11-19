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


def host_exist(route, config):
    hosts_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
    hosts_list = []
    for onos_host in hosts_dict["hosts"]:
        hosts_list.append(onos_host["id"])

    if route[1] in hosts_list and route[-1] in hosts_list:
        return True

    return False


def devices_exist(route, devices_dict):
    devices_list = []
    for device in devices_dict["devices"]:
        devices_list.append(["id"])

    for device in route:
        if device not in devices_list:
            return False

    return True


def is_host_link(host, device, hosts_dict):
    for onos_host in hosts_dict["hosts"]:
        if onos_host["id"] == host:
            for locations in onos_host["locations"]:
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
    hosts_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
    links_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/links"), config["username"], config["password"])
    devices_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/devices"), config["username"], config["password"])

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
