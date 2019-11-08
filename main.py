from flask import Flask, redirect, url_for, request, render_template, send_file, jsonify, make_response
import requests, datetime, shutil, os, glob, uuid, json, onos_connect, reroute

app = Flask(__name__)

config = {}

def load_json(filename):
    with open(filename) as f:
        return json.load(f)
    
def load_config():
    global config
    try :
        config = load_json("config.json")
    except:
        config = load_json("config-default.json")
    



@app.route('/api/get_intents', methods=['GET'])
def get_intents():
    routing_dict = reroute.generate_routes(config)
    return jsonify(reroute.generate_intents(routing_dict, config))



if __name__ == '__main__':
    load_config()
    app.run(host='0.0.0.0')