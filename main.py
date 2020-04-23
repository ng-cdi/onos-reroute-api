import requests
import datetime
import shutil
import os
import sys
import glob
import uuid
import json
import logging
from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response, abort
from configs import Configs
from spp_manager import SppManager
from reroute import Reroute
from onos_api import OnosConnect
from users import Users

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
spp_manager =  SppManager()
users = Users()
# config = confs.get_config()
# layers = confs.get_layers()

def load_json(request):
    try:
        loaded_dict = json.loads(request.get_data().decode())
        if not users.authenticate(loaded_dict.get("api_key")):
            abort(401, description="Could not authenticate with the key provided")
    except:
        abort(400, description="Could not parse the json provided")
    
    return loaded_dict

@app.route('/api/push_spp', methods=['GET', 'POST'])
def push_spp():
    spp_data = load_json(request)
    spp_added = spp_manager.add_spp(spp_data, users)

    if spp_added:
        abort(406, description=spp_added)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}     



@app.route('/api/push_intent', methods=['GET', 'POST'])
def push_intent():
    new_intents = load_json(request)
    reroute = Reroute()
    routing_dict = reroute.generate_routes()

    if (reroute.is_intent(routing_dict, new_intents)):
        if not spp_manager.is_spp():
            routing_dict.update(new_intents)
            # logging.info(json.dumps(reroute.generate_intents(routing_dict, confs.get_config()), indent=4, sort_keys=True))
            logging.info(OnosConnect("/onos/v1/imr/imr/reRouteIntents").post(reroute.generate_intents(routing_dict)))
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
        else:
            abort(409, description="Could not modify Intents - Service Protection Period")
    else:
        abort(406, description="Could accept the intent provided")


@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    reroute = Reroute()
    routing_dict = reroute.generate_routes()
    return jsonify(reroute.generate_intents(routing_dict))

@app.route('/api/is_spp', methods=['GET'])
def get_spp():
    return json.dumps({'spp': spp_manager.is_spp()}), 200, {'ContentType': 'application/json'}

@app.route('/api/get_routes', methods=['GET', 'POST'])
def get_routes():
    key = load_json(request)
    # key = {}
    # key["key"] = "00:00:00:00:00:01/None00:00:00:00:00:07/None"
    reroute = Reroute()
    routes = reroute.generate_host_to_host_routes(key.get("key"))
    return jsonify(routes)

@app.route('/api/get_config', methods=['GET'])
def get_config():
    return jsonify(Configs("json/config.json", "config-default.json").get_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
