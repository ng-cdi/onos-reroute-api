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

app = Flask(__name__)

config = {}


def load_json(filename):
    with open(filename) as f:
        return json.load(f)


def load_config():
    global config
    try:
        config = load_json("config.json")
    except:
        config = load_json("config-default.json")


@app.route('/api/push_intent', methods=['GET', 'POST'])
def push_intent():
    new_intents = json.loads(request.json)
    print(new_intents)

    routing_dict = reroute.generate_routes(config)

    if (!reroute.is_intent(routing_dict, new_intents)):

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    routing_dict = reroute.generate_routes(config)
    return jsonify(reroute.generate_intents(routing_dict, config))


if __name__ == '__main__':
    load_config()
    app.run(host='0.0.0.0')
