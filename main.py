from flask import Flask, redirect, url_for, request, render_template, send_file
import requests, datetime, shutil, os, glob, uuid, json, onos_connect

app = Flask(__name__)

config = ""

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
    
    return make_response("UUID Not Found", 403)


if __name__ == '__main__':
    load_config()
    app.run(host='0.0.0.0')