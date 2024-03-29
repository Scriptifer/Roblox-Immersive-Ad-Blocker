from flask import Flask, request, Response, jsonify
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import datetime
import platform
import os
import subprocess
import requests
import socket
import json
import ctypes
import ssl
import sys
import psutil
import atexit
system = platform.system()
robloxgameswithads = []
if system != "Windows":
    print("Only Windows is supported.")
    exit(1)

is_open = False
def get_certificate(hostname, ip_address, port=443):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with socket.create_connection((ip_address, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert_pem = ssl.DER_cert_to_PEM_cert(ssock.getpeercert(True))
    return cert_pem

def is_admin():
    try:
        with open("C:\\Program Files\\test.txt", "w") as f:
            f.write("Test")
        os.remove("C:\\Program Files\\test.txt")
        return True
    except PermissionError:
        return False

def is_roblox_open():
    for proc in psutil.process_iter():
        if "RobloxPlayerBeta.exe" in proc.name():
            return True
    return False

def elevate_privileges():
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)

if is_roblox_open():
    print("Please run this script before Roblox.")
    exit(1)

if not is_admin():
    elevate_privileges()
    exit(0)
 
if is_roblox_open():
    print("Please run this script before Roblox.")
    exit(1)

rbx_ip = socket.gethostbyname("apis.roblox.com")
connectToAServer = input("Would you like to connect to a Roblox immersive ad blocking server via entering IP address of the server? Note: the server will be able to see your cookies\n").lower().startswith("y")
if connectToAServer:
    rbx_ip = input("Please enter the server's ip address: ")
else:
    print("Locally hosting server and connecting to it.")

print("Please wait before opening Roblox..")
if not os.path.exists("games.json"):
    with open("games.json", "w") as f:
        f.write("[]")

else:
    with open("games.json", "r") as f:
        robloxgameswithads = json.load(f)


if rbx_ip == "127.0.0.1":
    print("It looks like last session was not able to cleanup properly, cleaning up now.")
    subprocess.run(["py", "cleanup.py"])
    rbx_ip = socket.gethostbyname("apis.roblox.com")

if rbx_ip == "127.0.0.1":
    print("Cleanup failed")
    exit(1)

if not connectToAServer:
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'roblox.com'),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'Roblox Corporation')
    ])
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(subject)
    builder = builder.not_valid_before(datetime.datetime.utcnow())
    builder = builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(private_key.public_key())
    builder = builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u'apis.roblox.com')]),
        critical=False,
    )
    
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=None), critical=True,
    )
    
    certificate = builder.sign(
        private_key=private_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )
    with open("certificate.pem", "wb") as cert_file:
        cert_bytes = certificate.public_bytes(serialization.Encoding.PEM)
        cert_file.write(cert_bytes)
    
    with open("private.key", "wb") as key_file:
        key_file.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        ))
    
else:
    with open("certificate.pem", "wb") as cert_file:
        cert_bytes = get_certificate("apis.roblox.com", rbx_ip).encode('utf-8')
        cert_file.write(cert_bytes)
    
    
subprocess.run(["certutil", "-addstore", "Root", "certificate.pem"])
certSerialNumber = x509.load_pem_x509_certificate(cert_bytes, default_backend()).serial_number
certSerialNumber = certSerialNumber.to_bytes((certSerialNumber.bit_length() + 7) // 8, 'big').hex()
with open("certificate.pem", "r") as file:
    pem_certificate = file.read()
    print(pem_certificate)

appdata_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Roblox')
if not os.path.isdir(appdata_dir):
    print(f"Error: Roblox directory '{appdata_dir}' not found.")
    exit(1)

def find_cacerts(directory):
    cacerts = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == "cacert.pem":
                cacerts.append(os.path.join(root, file))
    return cacerts

cacert_paths = find_cacerts(appdata_dir)
bloxstrap_dir = os.path.join(os.getenv('LOCALAPPDATA'), 'Bloxstrap')
if os.path.isdir(bloxstrap_dir):
    cacert_paths2 = find_cacerts(bloxstrap_dir)
    for cacert_path in cacert_paths2:
        cacert_paths.append(cacert_path)


if not cacert_paths:
    print("Error: No cacert.pem files found.")
    exit(1)

old_cacerts = {}
for cacert_path in cacert_paths:
    with open(cacert_path, 'r') as f:
        old_cacerts[cacert_path] = f.read()
    
    with open(cacert_path, 'a') as f:
        f.write("\n==================================\n"+pem_certificate)
    

with open("C:\\Windows\\System32\\drivers\\etc\\hosts", 'r') as f:
        old_hosts = f.read()

with open("C:\\Windows\\System32\\drivers\\etc\\hosts", 'a') as f:
    if connectToAServer:
        f.write("\n"+rbx_ip+"    apis.roblox.com\n0.0.0.0    advertise.roblox.com")
    else:
        f.write("\n127.0.0.1    apis.roblox.com\n0.0.0.0    advertise.roblox.com")
    

def cleanup():
    hosts_path = "C:\\Windows\\System32\\drivers\\etc\\hosts"
    with open(hosts_path, 'w') as f:
        f.write(old_hosts)
    
    for cacert, value in old_cacerts.items():
        with open(cacert, 'w') as f:
            f.write(value)


    subprocess.run(["certutil", "-delstore", "Root", certSerialNumber])
    os.remove("certificate.pem")
    if not connectToAServer:
        os.remove("private.key")
    
    exit(0)

app = Flask(__name__)
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
def catch_all(path):
    target_url = f'https://{rbx_ip}/{path}'
    query_params = request.args
    query_params_str = "&".join([f"{key}={value}" for key, value in query_params.items()])
    query_data = "?" + query_params_str if query_params_str else ""
    method = request.method
    headers = request.headers
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

if connectToAServer:
    print("Now you can open Roblox!")
    atexit.register(cleanup)
    try:
        while True:
            pass
        
    finally:
        print("Cleaning up..")
    
if __name__ == '__main__' and not connectToAServer:
    context = ('certificate.pem', 'private.key')
    try:
        print("Now you can open Roblox!")
        atexit.register(cleanup)
        app.run(host='localhost', port=443, ssl_context=context)
    finally:
        print("Cleaning up..")
