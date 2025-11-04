import requests
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json
import sys
import yaml
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def config_devices_router():
    with open(f'device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']

        for device in devices_list:
            device_router_config_dict = {"tailf-ned-cisco-ios:router": device["router"]}

            config_device_router_url = f"{nso_restconf_base_url}/tailf-ncs:devices/device={device['name']}/config/tailf-ned-cisco-ios:router"

            r = requests.put(config_device_router_url,
                             auth=auth_info,
                             json=device_router_config_dict,
                             headers=headers_json,
                             verify=False)
            if not r.ok:
                try:
                    json_result = r.json()
                    print(json_result)
                except requests.exceptions.JSONDecodeError:
                    pass
                sys.exit(1)


"""
{
  "tailf-ned-cisco-ios:router": {
    "ospf": [
      {
        "id": 1,
        "router-id": "1.1.1.1",
        "network": [
          {
            "ip": "192.168.1.0",
            "mask": "0.0.0.255",
            "area": 0
          }
        ]
      }
    ]
  }
}
"""
config_devices_router()