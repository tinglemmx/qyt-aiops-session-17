import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import pprint

from qyt_libs import qytang_ping, qytang_ssh


pp = pprint.PrettyPrinter(indent=4)

def anarylize_interface_result(result) -> dict:
    interface_prefix = ['eth', 'lo', 'tun', 'br','wwan']
    interfaces_info = {}
    result_list = result.strip().split('\n')
    tmp_interface_name = ''
    for line in result_list[3:]:
        _line = line.strip()
        _line_list = _line.split()        
        if any(i in _line_list[0] for i in interface_prefix):
            tmp_interface_name = _line_list[0]
            interfaces_info[tmp_interface_name] = []
            if _line_list[1] !=  '-':
                interfaces_info[tmp_interface_name].append(_line_list[1].strip())
        else:
            if _line_list[0] !=  '-':
                interfaces_info[tmp_interface_name].append(_line_list[0].strip())
    return interfaces_info

def get_interfaces_info(host_list, username, password, port=22):
    interface_info = {}
    for ip in host_list:
        if qytang_ping(ip):
            print(f'{ip} 可达')
            result = qytang_ssh(ip, username, password, port, 'vbash -ic "show interface"')
            interface_info[ip] = anarylize_interface_result(result) 
        else:
            print(f'{ip} 不可达')
            interface_info[ip] = {}
    return interface_info
    
if __name__ == '__main__':
    host_list = ["172.17.9.20", "192.168.3.100"]
    pp.pprint(get_interfaces_info(host_list, username = 'vyos', password = 'Cisc0123@'))