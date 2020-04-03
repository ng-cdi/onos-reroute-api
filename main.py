from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response
import requests
import datetime
import shutil
import os
import sys
import glob
import uuid
import json
import logging
from configs import Configs
from onos_api import OnosConnect
from reroute import Reroute

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
# confs = Configs()
# config = confs.get_config()
# layers = confs.get_layers()

@app.route('/api/push_intent', methods=['GET', 'POST'])
def push_intent():
    new_intents = json.loads(request.json)
    print(new_intents)
    reroute = Reroute()
    routing_dict = reroute.generate_routes()

    if (reroute.is_intent(routing_dict, new_intents)):
        routing_dict.update(new_intents)
        # logging.info(json.dumps(reroute.generate_intents(routing_dict, confs.get_config()), indent=4, sort_keys=True))
        logging.info(OnosConnect("/onos/v1/imr/imr/reRouteIntents").post(reroute.generate_intents(routing_dict)))
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'unsuccesful': False}), 406, {'ContentType': 'application/json'}


@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    reroute = Reroute()
    routing_dict = reroute.generate_routes()
    return jsonify(reroute.generate_intents(routing_dict))

@app.route('/api/get_routes', methods=['GET', 'POST'])
def get_routes():
    key = json.loads(request.json)
    key = {}
    key["key"] = "00:00:00:00:00:01/None00:00:00:00:00:07/None"
    reroute = Reroute()
    routes = reroute.generate_host_to_host_routes(key.get("key"))
    return jsonify(routes)

@app.route('/api/get_config', methods=['GET'])
def get_config():
    return jsonify(Configs("json/config.json", "config-default.json").get_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
