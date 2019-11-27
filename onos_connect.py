import base64
import json
import urllib.request


def auth_http(url, uname, passwd):
    request = urllib.request.Request(url)
    base64string = base64.encodestring(
        ('%s:%s' % (uname, passwd)).encode()).decode().replace('\n', '')
    request.add_header('Authorization', 'Basic %s' % base64string)
    return request


def onos_get(url, uname, passwd):
    request = auth_http(url, uname, passwd)
    response = urllib.request.urlopen(request)
    return json.loads(response.read())


def onos_post(url, uname, passwd, json_data):
    request = auth_http(url, uname, passwd)
    request.add_header('Content-Type', 'application/json')
    response = urllib.request.urlopen(request, data=bytes(json.dumps(json_data), encoding="utf-8"))
    return json.loads(response.read())


def url_builder(host, port, api):
    url = "http://" + host + ":" + port + api
    return url
