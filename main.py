import requests
import datetime
import shutil
import os
import sys
import glob
import uuid
import json
import logging, coloredlogs
from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response, abort
from configs import Configs
from spp_manager import SppManager
from reroute import Reroute
from onos_api import OnosConnect
from users import Users
from intent import Intent
from testperf import TestPerf

logger = logging.getLogger(__name__)
coloredlogs.install(level='INFO')


app = Flask(__name__)
spp_manager =  SppManager()
users = Users()
# config = confs.get_config()
# layers = confs.get_layers()

def auth_key(key):
    if not users.authenticate(key):
        abort(401, description="Could not authenticate with the key provided")

def load_json(request):
    try:
        loaded_dict = json.loads(request.get_data().decode())
        auth_key(loaded_dict.get("api_key"))
    except:
        abort(400, description="Could not parse the json provided")
    
    return loaded_dict

# REST Endpoints

@app.route('/api/push_spp', methods=['GET', 'POST'])
def push_spp():
    spp_data = load_json(request)
    spp_added = spp_manager.add_spp(spp_data, users)

    if spp_added:
        abort(406, description=spp_added)

    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}     

@app.route('/api/get_spp', methods=['GET', 'POST'])
def get_spp():
    # load_json(request)
    return jsonify(spp_manager.export())   

@app.route('/api/push_intent', methods=['GET', 'POST'])
def push_intent():
    new_intents = load_json(request)
    logger.info("[push_intent] Recieved New Intent: " + json.dumps(new_intents, indent=4, sort_keys=True))
    api_key = new_intents.get("api_key")
    reroute = Reroute()
    new_intents = reroute.routing_abs(new_intents)
    routing_dict = reroute.generate_routes()

    if (reroute.is_intent(routing_dict, new_intents)):
        if spp_manager.is_spp(users, api_key):
            abort(409, description="Could not modify Intents - Service Protection Period")
        else:
            routing_dict.update(new_intents)
            # logger.info(json.dumps(reroute.generate_intents(routing_dict), indent=4, sort_keys=True))
            logger.info(OnosConnect("/onos/v1/imr/imr/reRouteIntents").post(reroute.generate_intents(routing_dict)))
            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

    else:
        logger.error("[Main] Could not ")
        abort(406, description="Could accept the intent provided")


@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    reroute = Reroute()
    routing_dict = reroute.generate_routes()
    return jsonify(reroute.generate_intents(routing_dict))

@app.route('/api/is_spp', methods=['GET'])
def is_spp():
    return jsonify({"spp":spp_manager.is_spp()})

@app.route('/api/get_routes', methods=['GET', 'POST'])
def get_routes():
    key = load_json(request)
    # key = {}
    # key["key"] = "00:00:00:00:00:01/None00:00:00:00:00:07/None"
    logger.info("[get_routes] Recieved New Routes Request: " + json.dumps(key, indent=4, sort_keys=True))
    reroute = Reroute()
    routes = reroute.generate_host_to_host_routes(key.get("key"))
    logger.info("[get_routes] Returned Routes " + json.dumps(routes, indent=4, sort_keys=True))
    return jsonify(routes)

@app.route('/api/get_config', methods=['GET'])
def get_config():
    return jsonify(Configs("json/config.json", "config-default.json").get_config())

@app.route('/api/get_users', methods=['GET'])
def get_users():
    return jsonify(users.get_users())

# HTML Endpoints

@app.route('/user_table', methods=['GET'])
def user_table():
    return render_template("users.html", table = users.get_user_table())

@app.route('/spp_table', methods=['GET'])
def spp_table():
    return render_template("spp.html", spp_status = spp_manager.get_active_button(), table = spp_manager.get_spp_table())

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        api_key = request.form['api_key']
        # print(api_key)
        auth_key(api_key)
        intent = Intent(request.form['intent'], api_key, users, spp_manager)
        parse_errs = intent.parse()
        if parse_errs: abort(400, description=parse_errs)
        
        return render_template('accepted.html')

    else:
        return render_template('index.html', spp_status = spp_manager.get_active_button())

@app.route('/testperf', methods=['POST', 'GET'])
def test_perf():
    TestPerf()
    return render_template('testperf.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0')
