from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response
import requests
import datetime
import shutil
import os
import sys
import glob
import uuid
import json
import onos_connect
import reroute
import logging
from configs import *

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
confs = Configs()
# config = confs.get_config()
# layers = confs.get_layers()

@app.route('/api/push_intent', methods=['GET', 'POST'])
def push_intent():
    new_intents = json.loads(request.json)
    print(new_intents)

    routing_dict = reroute.generate_routes(confs.get_config())

    if (reroute.is_intent(routing_dict, new_intents, confs.get_config())):
        routing_dict.update(new_intents)
        # logging.info(json.dumps(reroute.generate_intents(routing_dict, confs.get_config()), indent=4, sort_keys=True))
        logging.info(onos_connect.onos_post(onos_connect.url_builder(confs.get_config().get("host"), confs.get_config().get("port"), "/onos/v1/imr/imr/reRouteIntents"), confs.get_config().get("username"), confs.get_config().get("password"), reroute.generate_intents(routing_dict, confs.get_config())))
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'unsuccesful': False}), 406, {'ContentType': 'application/json'}


@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    routing_dict = reroute.generate_routes(confs.get_config())
    return jsonify(reroute.generate_intents(routing_dict, confs.get_config()))

@app.route('/api/get_config', methods=['GET'])
def get_config():
    return jsonify(confs.get_config())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
