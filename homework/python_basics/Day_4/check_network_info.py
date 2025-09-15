import os
import ipaddress
import re
def run_cmd(cmd:str):
    result = os.popen(cmd).read()
    return result

def get_ip_info():
    cmd = 'ifconfig eth0'
    fields = [
        ("ipv4_add", "ip_address"),
        ("netmask", "netmask"),
        ("broadcast", "broadcast"),
        ("mac_addr", "mac_address"),
    ]
    result = run_cmd(cmd)
    format_str = result.replace('\n', ' ')
    pattern = re.compile(
        r'.*inet\s+(?P<ip_address>\d{1,3}(?:\.\d{1,3}){3})\s+'
        r'netmask\s+(?P<netmask>\d{1,3}(?:\.\d{1,3}){3})\s+'
        r'broadcast\s+(?P<broadcast>\d{1,3}(?:\.\d{1,3}){3}).*'
        r'ether\s+(?P<mac_address>[0-9a-f]{2}(?::[0-9a-f]{2}){5}).*'
    )
    match = pattern.match(format_str)
    if match:
        return match.groupdict(),fields
    return None,fields

def print_info(info,fields=None):
    if fields == None:
        raise ValueError('fields is None')
    max_len = max(len(x[0]) for x in fields)
    field_width = max_len + 5
    if info:
        for label, key in fields:
            print(f'{label:<{field_width}}: {info.get(key,"N/A")}')
    else:
        print('No match')

def generate_gateway_ip_from_ipinfo(ip_info):
    if ip_info:
        net = ipaddress.ip_network(f"{ip_info['ip_address']}/{ip_info['netmask']}", strict=False)
        first_ip = next(net.hosts()) 
        print(f'\n我们假设网关IP地址为接口地址所在网段的第一个地址。因此网关IP地址为：{first_ip} \n')
        return first_ip
    else:
        raise ValueError('ip_info is None')
    
def get_default_gateway(ip_info=None):
    print('从路由表获取网关IP地址...')
    cmd = 'ip route show'
    result = run_cmd(cmd)
    pattern = re.compile(r'default via (\d{1,3}(?:\.\d{1,3}){3})')
    match = pattern.search(result)
    if match:
        gateway_ip = match.group(1)
        try:
            ipaddress.ip_address(gateway_ip)
            print(f'从路由表获取网关IP地址 {gateway_ip} 有效！')
            return gateway_ip
        except ValueError:
            print(f'从路由表获取网关IP地址 {gateway_ip} 无效！')
    print('从路由表获取网关IP地址失败！ 尝试从接口信息生成网关IP地址...')
    return str(generate_gateway_ip_from_ipinfo(ip_info))

def check_gateway_ip(gateway_ip):
    if gateway_ip:
        print(f'Checking default gateway IP address({gateway_ip})...')
        ping_result = run_cmd(f'ping -c 1 -W 1 {gateway_ip}')
        re_ping_result = re.search(r'1\s+received', ping_result)
        if re_ping_result:
            print(f'网关可达！')
        else:
            print(f'网关不可达！')
    else:
        raise ValueError('Default gateway is not set')
    
if __name__ == '__main__':
    ip_info,fields = get_ip_info()
    print_info(ip_info,fields)
    gateway_ip = get_default_gateway(ip_info)
    check_gateway_ip(gateway_ip)