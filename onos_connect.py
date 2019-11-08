import base64, json, urllib.request

def auth_http(url, uname, passwd):
    request = urllib.request.Request(url)
    base64string = base64.encodestring(('%s:%s' % (uname, passwd)).encode()).decode().replace('\n', '')
    request.add_header('Authorization', 'Basic %s' % base64string)
    return request

def onos_get(url, uname, passwd):
    # try:
        request = auth_http(url, uname, passwd)
        response = urllib.request.urlopen(request)
        return json.loads(response.read())
    # except:
    #     return ""

def onos_post(url, uname, passwd, json_data):
    try:
        request = auth_http(url, uname, passwd)
        request.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(request, data=json_data)
        return json.loads(response.read())
    except:
        return ""

def url_builder(host, port, api):
    url = "http://" + host + ":" + port + api
    return url 