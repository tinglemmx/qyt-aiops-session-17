import os
import ipaddress
import re

def run_cmd(cmd:str):
    result = os.popen(cmd).read()
    return result

def print_default_gateway():
    print('从路由表获取网关IP地址...')
    cmd = 'route -n'
    result_list = run_cmd(cmd).split('\n')
    for line in result_list:
        pattern = re.compile(r'0.0.0.0\s+(\d{1,3}(?:\.\d{1,3}){3})\s+0.0.0.0\s+UG')
        match = pattern.search(line.strip())
        if match:
            gateway_ip = match.group(1)
            try:
                ipaddress.ip_address(gateway_ip)
                print(f'网关为：{gateway_ip} ')
                return gateway_ip
            except ValueError:
                continue
    print('未找到默认网关IP地址')
    

if __name__ == '__main__':
    print_default_gateway()