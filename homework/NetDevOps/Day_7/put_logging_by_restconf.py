import requests
from requests.auth import HTTPBasicAuth
import urllib3
import json

# 禁用 HTTPS 证书告警（实验环境常用）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://192.0.2.210:443/restconf/data/Cisco-IOS-XE-native:native/logging"
username = "admin" 
password = "cisco123" 

headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

data = {
  "Cisco-IOS-XE-native:logging": {
    "trap": {"severity": "debugging"},
    "host": {
      "ipv4-host-list": [
        {"ipv4-host": "192.168.100.1"},
        {"ipv4-host": "192.168.100.5"},
        {"ipv4-host": "192.168.100.3"}
      ]
    },
    "hostip": "192.168.100.1"
  }
}

resp = requests.put(
    url,
    headers=headers,
    data=json.dumps(data),
    auth=HTTPBasicAuth(username, password),
    verify=False
)

print(resp.status_code, resp.text)