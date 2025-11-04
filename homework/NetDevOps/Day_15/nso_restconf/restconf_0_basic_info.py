from requests.auth import HTTPBasicAuth
import base64
import os
nso_username = os.getenv('nso_username')
nso_password = os.getenv('nso_password')
nso_restconf_base_url = os.getenv('ci_restconf_url')

# nso_username = 'ncsuser'
# nso_password = 'Cisc0123'
# nso_restconf_base_url = "https://172.17.9.217:8888/restconf/data"

# Gitlab CICD
script_path = './nso_restconf/'

auth_info = HTTPBasicAuth(nso_username, nso_password)
# token = base64.b64encode(f"{nso_username}:{nso_password}".encode()).decode()
headers_json = {'Accept': 'application/yang-data+json', 'Content-Type': 'application/yang-data+json'}
headers_xml = {'Accept': 'application/yang-data+xml', 'Content-Type': 'application/yang-data+xml'}