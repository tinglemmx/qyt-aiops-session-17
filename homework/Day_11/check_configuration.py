import warnings
from cryptography.utils import CryptographyDeprecationWarning

warnings.filterwarnings("ignore", category=CryptographyDeprecationWarning)

import pprint
import hashlib
import time

from qyt_libs import qytang_ssh

def qytang_get_config(ip, username, password,port=22):
    result = qytang_ssh(ip, username, password, port, 'vbash -ic "show configuration commands | no-more"')
    return result

def qytang_check_diff(ip,username, password,port=22):
    first_time = True
    base_result_md5 = ''
    while True:
        current_result = qytang_get_config(ip, username, password, port)
        # print(current_result)
        m = hashlib.md5()
        m.update(current_result.encode('utf-8'))
        current_result_md5 = m.hexdigest()
        print(current_result_md5)
        if first_time:
            base_result_md5 = current_result_md5
            first_time = False
        elif current_result_md5 != base_result_md5:
            print("MD5 value changed")
            break
        time.sleep(5)

if __name__ == '__main__':
    qytang_check_diff('172.17.9.216', 'vyos', 'vyos')