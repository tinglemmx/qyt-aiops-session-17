import requests
from requests.auth import HTTPBasicAuth
import urllib3

# 禁用 HTTPS 证书告警（实验环境常用）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# === RESTCONF 访问配置 ===
url = "https://192.0.2.210:443/restconf/data/Cisco-IOS-XE-process-cpu-oper:cpu-usage/cpu-utilization/five-seconds"
username = "admin" 
password = "cisco123" 

# === RESTCONF Header ===
headers = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# === 发送 GET 请求 ===
response = requests.get(
    url,
    auth=HTTPBasicAuth(username, password),
    headers=headers,
    verify=False  # 实验设备一般使用自签名证书
)

# === 解析返回 ===
if response.status_code == 200:
    print("请求成功")
    print(response.json())
else:
    print(f"请求失败，状态码: {response.status_code}")
    print(response.text)
