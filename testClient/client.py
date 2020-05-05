import base64
import json
import requests

# Send JSON


def post_json(url, reroute_JSON):
    try:
        r = requests.post(url, data=reroute_JSON)
        print(r.status_code)
    except IOError as e:
        print(e)
        return

# Load JSON from file


def main():
    with open("reroute.json", 'r') as f:
        reroute_JSON = json.load(f)
        post_json('http://api.demo.ng-cdi.com/api/push_intent',
                  json.dumps(reroute_JSON))


main()
