from flask import Flask, request, Response, jsonify
import requests
import os
import socket
import json
robloxgameswithads = []
if not os.path.exists("games.json"):
    with open("games.json", "w") as f:
        f.write("[]")

else:
    with open("games.json", "r") as f:
        robloxgameswithads = json.load(f)


rbx_ip = socket.gethostbyname("apis.roblox.com")
app = Flask(__name__)
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def catch_all(path):
    target_url = f'https://{rbx_ip}/{path}'
    query_params = request.args
    query_params_str = "&".join([f"{key}={value}" for key, value in query_params.items()])
    query_data = "?" + query_params_str if query_params_str else ""
    method = request.method
    headers = dict(request.headers)
    headers["Host"] = "apis.roblox.com"
    if query_data != "?":
        target_url = target_url+query_data

    if path == "ads/v1/serve-ads":
        universe_id = request.headers.get("Roblox-Universe-Id")
        if universe_id:
            if not (universe_id in robloxgameswithads):
                robloxgameswithads.append(universe_id)
                with open("games.json", "w") as f:
                    json.dump(robloxgameswithads, f)
            
        try:
            payload = request.get_json()
            if payload:
                adSlots = payload.get("adSlots")
                adFulfillments = []
                for i in range(len(adSlots)):
                    adFulfillments.append(None)

                return jsonify({"adFulfillments": adFulfillments, "noFillReason": 2})
            
        except Exception as e:
            print("Error:", e)
            return "Something went wrong", 500
        
    
    response = requests.request(method, target_url, headers=headers, data=request.get_data(), cookies=request.cookies, allow_redirects=False, verify=False)
    contentresponse = response.content
    if path == "experience-guidelines-api/experience-guidelines/get-age-recommendation":
        payload = request.get_json()
        universeId = payload.get("universeId")
        if universeId in robloxgameswithads:
            responseJSON = json.loads(contentresponse)
            responseJSON["ageRecommendationDetails"]["summary"]["ageRecommendation"]["displayName"] = responseJSON["ageRecommendationDetails"]["summary"]["ageRecommendation"]["displayName"]+" - Contains ads"
            contentresponse = json.dumps(responseJSON)
        
    return Response(contentresponse, status=response.status_code, content_type=(response.headers.get('Content-Type') or "text/plain"), headers=response.headers.items())

if __name__ == '__main__':
    try:
        app.run(host='localhost', port=8888)
    finally:
        print("Cleaning up..")
