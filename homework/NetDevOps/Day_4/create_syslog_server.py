import requests
import json
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(InsecureRequestWarning)


class ASAClient:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.base_url = f"https://{host}"
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "REST API Agent"
        }

    def post(self, api_path, payload):
        """
        发送 POST 请求
        """
        url = f"{self.base_url}{api_path}"
        try:
            resp = requests.post(
                url,
                headers=self.headers,
                auth=(self.username, self.password),
                verify=False,
                json=payload
            )
            try:
                return resp.status_code, resp.json()
            except ValueError:
                return resp.status_code, resp.text
        except requests.RequestException as e:
            return None, str(e)

    def configure_syslog_server(self, ip, interface="MGMT", port=514, protocol="UDP",
                                emblem_enabled=False, secure_enabled=False):
        payload = {
            "ip": {
                "kind": "IPv4Address",
                "value": ip
            },
            "interface": {
                "kind": "objectRef#Interface",
                "name": interface
            },
            "port": port,
            "emblemEnabled": emblem_enabled,
            "secureEnabled": secure_enabled,
            "protocol": protocol
        }
        return self.post("/api/logging/syslogserver", payload)


if __name__ == "__main__":
    asa = ASAClient("172.17.9.215", "admin", "cisco132")

    # 配置 syslog server
    status, resp = asa.configure_syslog_server(
        "172.17.9.220", port=1040, protocol="TCP")
    print("Status Code:", status)
    print(json.dumps(resp, indent=2) if isinstance(resp, dict) else resp)
