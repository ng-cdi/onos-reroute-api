import base64
import json
import requests
import time

# Send JSON



def post_json(url, reroute_JSON):
    try:
        r = requests.post(url, json=reroute_JSON)
        print("STATUS [" + str(r.status_code) + "]")
    except IOError as e:
        print(e)
        return

# Load JSON from file

def load_json(filename):
    with open(filename, 'r') as f:
        reroute_JSON = json.load(f)
        return reroute_JSON
        # 

def main():
    url = "http://127.0.0.1:5000/api/push_intent"
    bar = [
        "Polling traffic data...  [=     ]",
        "Polling traffic data...  [ =    ]",
        "Polling traffic data...  [  =   ]",
        "Polling traffic data...  [   =  ]",
        "Polling traffic data...  [    = ]",
        "Polling traffic data...  [     =]",
        "Polling traffic data...  [    = ]",
        "Polling traffic data...  [   =  ]",
        "Polling traffic data...  [  =   ]",
        "Polling traffic data...  [ =    ]",
    ]
    i = 0
    end_time = time.time() + 20
    while time.time() < end_time:
        print(bar[i % len(bar)], end="\r")
        time.sleep(.1)
        i += 1
    
    print("Polling traffic data...  [=     ]\nCalculating new intents...")
    time.sleep(0.5)
    reroute = load_json("reroute.json")
    print(json.dumps(reroute, indent=4, sort_keys=True))
    print("Sending to server...")
    post_json(url, json.dumps(reroute))
    input("Press any key to close...")
    post_json(url, json.dumps(load_json("reset.json")))
    


main()
