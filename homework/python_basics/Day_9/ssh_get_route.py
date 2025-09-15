import ipaddress
import re

from paramiko_ssh import qytang_ssh

def ssh_get_route(ip, user, passwd, port=22):
    command = "vbash -ic 'route -n'"
    result = qytang_ssh(ip, user, passwd, port, command)
    # print(result)
    result_list = result.split('\n')
    for line in result_list:
        pattern = re.compile(r'0.0.0.0\s+(\d{1,3}(?:\.\d{1,3}){3})\s+0.0.0.0\s+UG')
        match = pattern.search(line.strip())
        if match:
            gateway_ip = match.group(1)
            try:
                ipaddress.ip_address(gateway_ip)
                # print(f'网关为：{gateway_ip} ')
                return gateway_ip + '\n\n'
            except ValueError:
                continue
    print('未找到默认网关IP地址')

if __name__ == '__main__':
    print(qytang_ssh('172.17.9.215', 'vyos', 'Cisco@1234'))
    print(qytang_ssh('172.17.9.215', 'vyos', 'Cisco@1234', cmd='pwd'))
    print('网关为：')
    print(ssh_get_route('172.17.9.215', 'vyos', 'Cisco@1234'))