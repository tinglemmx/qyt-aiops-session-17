import requests
from restconf_0_basic_info import nso_restconf_base_url, auth_info, headers_json
import sys
import yaml


def config_devices_interface():
    with open(f'device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']

        for device in devices_list:
            device_interface_config_dict = {"tailf-ned-cisco-ios:interface": device["interface"]}

            config_device_interface_url = f"{nso_restconf_base_url}/tailf-ncs:devices/device={device['name']}/config/tailf-ned-cisco-ios:interface"

            r = requests.put(config_device_interface_url,
                             auth=auth_info,
                             json=device_interface_config_dict,
                             headers=headers_json,
                             verify=False
                             )
            if not r.ok:
                try:
                    json_result = r.json()
                    print(json_result)
                except requests.exceptions.JSONDecodeError:
                    pass
                sys.exit(1)

config_devices_interface()
"""
{
    "tailf-ned-cisco-ios:interface": {
        "GigabitEthernet": [
            {
                "name": "1",
                "negotiation": {
                    "auto": true
                },
                "ip": {
                    "address": {
                        "primary": {
                            "address": "172.16.1.1",
                            "mask": "255.255.255.0"
                        }
                    }
                }
            },
            {
                "name": "2",
                "negotiation": {
                    "auto": true
                },
                "ip": {
                    "address": {
                        "primary": {
                            "address": "192.168.1.1",
                            "mask": "255.255.255.0"
                        }
                    }
                }
            }
        ]
    }
}
"""