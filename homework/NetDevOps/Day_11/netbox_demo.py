
import pynetbox
import pprint
from jinja2 import Environment, FileSystemLoader
from netmiko import ConnectHandler
from pathlib import Path
import ipaddress

pp = pprint.PrettyPrinter(indent=4)

BASE_DIR = Path(__file__).resolve().parent

netbox_url = "http://172.17.9.210:8000"
netbox_token = "b144e7986c15e29cf274bfc511a6d5e2cd62c8b9"

env = Environment(loader=FileSystemLoader(BASE_DIR),
                  trim_blocks=True,
                  lstrip_blocks=True)
template = env.get_template('config_template.j2')

# 产生NETBOX API连接实例
nb = pynetbox.api(url=netbox_url, token=netbox_token)

router_username = 'admin'
router_password = 'Cisc0123'


def get_device_info(site, rack):
    all_devices = nb.dcim.devices.filter(site=site, rack=rack)
    devices_info_list = []
    # 迭代每一个设备, 构建device_dict字典, 并放入device_list列表
    for device in all_devices:
        device_dict = {}
        # pp.pprint(device.serialize())
        device_name = device.name
        device_dict['name'] = device_name
        device_dict['uuid'] = device.asset_tag
        device_dict['platform'] = device.platform.slug if device.platform else None
        device_dict['mgmt_ip'] = str(device.primary_ip4).split(
            '/')[0] if device.primary_ip4 else None
        _custom_fields = device.custom_fields
        if _custom_fields:
            device_dict['ospf_enabled'] = _custom_fields.get(
                'ospf_enabled', False)
            device_dict['ospf_router_id'] = _custom_fields.get(
                'ospf_router_id', None)
        interfaces = nb.dcim.interfaces.filter(device_id=device.id)
        interface_list = []
        for iface in interfaces:
            infterface_dict = {}
            interface_name = iface.name
            ip_address = nb.ipam.ip_addresses.get(
                device=device_name, interface_id=iface.id)
            if ip_address:
                net = ipaddress.IPv4Interface(ip_address)
                ip_address_cisco_style = (
                    str(net.ip), str(net.network.netmask))
                interface_dict = {"interface_name": interface_name,
                                  "ip_address": ip_address_cisco_style,
                                  "ospf_area": iface.custom_fields.get('ospf_area', None),
                                  "ospf_cost": iface.custom_fields.get('ospf_cost', None)
                                  }
                interface_list.append(interface_dict)
        device_dict['interfaces'] = interface_list
        devices_info_list.append(device_dict)
    return devices_info_list


def render_config(device_info):
    config_output = template.render(**device_info)
    return config_output


def push_config(device_info, config):
    device_params = {
        'device_type': 'cisco_ios',
        'host': device_info['mgmt_ip'],
        'username': router_username,
        'password': router_password,
    }
    net_connect = ConnectHandler(**device_params)
    output = net_connect.send_config_set(config.splitlines())
    net_connect.disconnect()
    return output


if __name__ == '__main__':
    print("Fetching device information from NetBox...")
    info = get_device_info('site1', 'rack01')
    for device_info in info:
        print('*'*6, "Processing device:", device_info['name'], '*'*6)
        pp.pprint(device_info)
        config = render_config(device_info)
        result = push_config(device_info, config)
        print(result)
