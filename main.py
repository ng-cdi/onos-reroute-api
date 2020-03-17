from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response
import requests
import datetime
import shutil
import os
import glob
import uuid
import json
import onos_connect
import reroute
import logging
import Configs

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

config = Configs.get_config()
layers =Configs.get_layers()

@app.route('/api/push_intent', methods=['GET', 'POST'])
def push_intent():
    new_intents = json.loads(request.json)
    print(new_intents)

    routing_dict = reroute.generate_routes(config)

    if (reroute.is_intent(routing_dict, new_intents, config)):
        routing_dict.update(new_intents)
        # logging.info(json.dumps(reroute.generate_intents(routing_dict, config), indent=4, sort_keys=True))
        logging.info(onos_connect.onos_post(onos_connect.url_builder(config.get("host"), config.get("port"), "/onos/v1/imr/imr/reRouteIntents"), config.get("username"), config.get("password"), reroute.generate_intents(routing_dict, config)))
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    else:
        return json.dumps({'unsuccesful': False}), 406, {'ContentType': 'application/json'}


@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    routing_dict = reroute.generate_routes(config)
    return jsonify(reroute.generate_intents(routing_dict, config))


if __name__ == '__main__':
    load_config()
    app.run(host='0.0.0.0')
