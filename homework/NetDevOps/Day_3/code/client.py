import requests
from pathlib import Path


base_dir = Path(__file__).parent / "certs"
url = "https://172.17.102.12:8443/run_command"
data = {"command": "ifconfig"}

resp = requests.post(
    url,
    json=data,
    cert=(base_dir / "client.crt", base_dir / "client.key"),
    verify=base_dir / "myCA.pem"
)
if resp.status_code == 200:
    print(resp.json().get("output"))
else:
    print(resp.status_code)