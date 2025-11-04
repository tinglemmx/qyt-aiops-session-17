from pprint import pprint
import urllib3
import requests
import yaml
from restconf_0_basic_info import nso_restconf_base_url, headers_json, auth_info
import sys
from deepdiff import DeepDiff

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# print("headers_json:",headers_json)
expected_config = None

def get_logging_setting():
    with open(f'device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']
        final_logging_result = []
        for device in devices_list:
            get_logging_config_url = f"{nso_restconf_base_url}/tailf-ncs:devices/device={device['name']}/config/tailf-ned-cisco-ios:logging"
            # print("url:",get_logging_config_url)
            r = requests.get(get_logging_config_url,
                             auth=auth_info,
                             headers=headers_json,
                             verify=False,
                             )
            if not r.ok:
                print(final_logging_result)
                try:
                    json_result = r.json()
                    print(json_result)
                except requests.exceptions.JSONDecodeError:
                    pass
                sys.exit(1)

            try:
                json_result = r.json()
                final_logging_result.append(json_result)
            except requests.exceptions.JSONDecodeError:
                final_logging_result.append(None)

        return final_logging_result


def put_logging_setting():
    with open(f'device_config_info.yaml') as f:
        config_info = yaml.load(f, Loader=yaml.FullLoader)
        devices_list = config_info['devices']
        global expected_config 
        expected_config = []
        final_logging_setting_result = []
        for device in devices_list:
            device_logging_config_dict = {
                "tailf-ned-cisco-ios:logging": device["logging"]}
            expected_config.append(device_logging_config_dict)
            config_device_logging_url = f"{nso_restconf_base_url}/tailf-ncs:devices/device={device['name']}/config/tailf-ned-cisco-ios:logging"

            r = requests.put(config_device_logging_url,
                             auth=auth_info,
                             json=device_logging_config_dict,
                             headers=headers_json,
                             verify=False)
            if not r.ok:
                try:
                    json_result = r.json()
                    print(json_result)
                except requests.exceptions.JSONDecodeError:
                    pass
            if r.text == '':
                final_logging_setting_result.append(f"{device['name']} logging 配置成功")
            else:
                final_logging_setting_result.append(r.text)
        return final_logging_setting_result

def validate_config(expected, actual):
    diff = DeepDiff(expected, actual, ignore_order=True)
    if diff:
        print("配置不一致")
        for k, v in diff.items():
            print(f"{k}: {v}")
        # 退出脚本，返回非零状态码 → pipeline 失败
        sys.exit(1)
    else:
        print("配置一致")


print('查看设备Logging配置:\n'),

pprint(get_logging_setting())

print('配置Logging:\n')

pprint(put_logging_setting())

print('\nLogging配置校验:\n')

validate_config(expected_config , get_logging_setting())

# import requests
# import json

# url = "https://172.17.9.217:8888/restconf/data/tailf-ncs:devices/device=C8Kv1/config/tailf-ned-cisco-ios:logging"

# payload={}
# headers = {
#    'Accept': 'application/yang-data+json',
# #    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
#    'Content-Type': 'application/yang-data+json',
#    'Authorization': 'Basic bmNzdXNlcjpDaXNjMDEyMw==',    用auth 也可以 直接Base64灌进去也可以
# #    'Host': '172.17.9.217:8888',
# #    'Connection': 'keep-alive'
# }

# response = requests.request("GET", url, headers=headers, data=payload, verify=False)

# print(response.text)
