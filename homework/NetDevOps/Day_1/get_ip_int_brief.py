import requests
from requests.auth import HTTPBasicAuth

url = "https://172.17.9.215/level/15/exec/-/show/ip/interface/brief/CR"

username = "admin"
password = "Cisc0123"

# 如果设备使用自签名证书，可以加 verify=False
resp = requests.get(url, auth=HTTPBasicAuth(username, password), verify=False)

# 检查状态
resp.raise_for_status()

# 输出结果
print(resp.text)
