import base64, json, urllib.request

def authenticated_http_req(url, uname, passwd):
    request = urllib.request.Request(url)
    base64string = base64.encodestring('%s:%s' % (uname, passwd)).replace('\n', '')
    request.add_header('Authorization', 'Basic %s' % base64string)
    return request

def json_get_req(url, uname, passwd):
    try:
        request = authenticated_http_req(url, uname, passwd)
        response = urllib.request.urlopen(request)
        return json.loads(response.read())
    except:
        return ""

def json_post_req(url, json_data):
    try:
        request = authenticated_http_req(url, uname, passwd)
        request.add_header('Content-Type', 'application/json')
        response = urllib.request.urlopen(request, data=json_data)
        return json.loads(response.read())
    except:
        return ""

def url_builder(host, port, api):
    url = host + ":" + port + api
    return url 