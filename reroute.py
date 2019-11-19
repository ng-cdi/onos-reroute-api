import json
import onos_connect
import logging

logging.basicConfig(level=logging.INFO)


def generate_routes(config):
    intents_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/intents"), config["username"], config["password"])
    hosts_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
    routing_dict = {}

    # Build initial dict of routes
    for intent in range(len(intents_dict["intents"])):
        key = intents_dict["intents"][intent]["key"]
        route = []
        route.append(key[:22])
        # 1 hop intents
        if len(intents_dict["intents"][intent]["resources"]) == 0:
            print("hit")
            for onos_host in hosts_dict["hosts"]:
                # Some hosts aren't listed in /v1/hosts.. try the reverse too
                if onos_host["id"] == key[:22] or onos_host["id"] == key[22:]:
                    if len(onos_host["locations"][0]["elementId"]) > 2:
                        route.append(onos_host["locations"][0]["elementId"])
                        print(onos_host["locations"][0]["elementId"])
                        break
        # Multi-hop intents
        else:
            for resource in range(len(intents_dict["intents"][intent]["resources"])):
                route.append(intents_dict["intents"][intent]["resources"][resource]["src"]["device"])
                route.append(intents_dict["intents"][intent]["resources"][resource]["dst"]["device"])
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
        devices_list.append(device["id"])

    for device in route:
        if device not in devices_list:
            logging.warning(device + ": Device not found")
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


def is_key(key, new_intents):
    src_host = key[:22]
    dst_host = key[22:]

    if new_intents[key][0] == src_host and new_intents[key][-1] == dst_host:
        return True

    return False


def is_route(route, config, key):
    hosts_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/hosts"), config["username"], config["password"])
    links_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/links"), config["username"], config["password"])
    devices_dict = onos_connect.onos_get(onos_connect.url_builder(
        config["host"], config["port"], "/onos/v1/devices"), config["username"], config["password"])

    # check host connections
    if not is_host_link(route[0], route[1], hosts_dict):
        logging.warning(
            key + ": There is no link between the src host and src device")
        return False

    if not is_host_link(route[-1], route[-2], hosts_dict):
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
    if not devices_exist(link_list, devices_dict):
        logging.warning(key + ": Device not found")
        return False

    dst_dev = link_list[-1]

    for i in range(len(link_list)):
        # Made it to the destination device
        if link_list[i] == dst_dev:
            logging.info(key + ": Multi-hop link exists")
            return True

        # Is there a link to the next device?
        if not is_link(link_list[i], link_list[i + 1], links_dict):
            logging.warning(key + ": No link between device " +
                            link_list[i] + " and device " + link_list[i + 1])
            return False

    return False


def is_intent(routing_dict, new_intents, config):
    for key in list(dict.fromkeys(new_intents)):
        # Too short for an intent
        if len(new_intents[key]) < 3:
            logging.warning(key + " is too short for an intent")
            return False
        if not is_key(key, new_intents):
            logging.warning(key + " does not match the hosts provided: " +
                            new_intents[key][0] + " and " + new_intents[key][-1])
            return False
        #  Does the key already exist?
        if key not in list(dict.fromkeys(routing_dict)):
            # Do the hosts exist?
            logging.info(
                key + " does not already exist in current intents list")
            if host_exist(new_intents[key], config):
                # Is it a valid route?
                if is_route(new_intents[key], config, key):
                    return True
                else:
                    return False
            else:
                logging.warning(key + " hosts do not exist on onos")
                return False
        else:
            # Is it a valid route?
            logging.info(key + " exists in current intents list")
            if is_route(new_intents[key], config, key):
                return True
    return False
