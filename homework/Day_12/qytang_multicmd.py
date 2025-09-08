import paramiko
import time

error_keywords = ['Invalid', 'error', 'failed', 'Error', 'Failed']
def qyang_multicmd(ip, username, password,cmd_list:list, port=22, enable='',wait_time=2,verbose=True ):
    client = paramiko.SSHClient()
    client.load_system_host_keys()  # 加载系统SSH密钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port, username, password, timeout=wait_time, compress=True)
    chan = client.invoke_shell() # 激活交互式shell
    time.sleep(1)
    chan.recv(65535)  

    for cmd in cmd_list:
        print(f"\n>>> {cmd}")  
        chan.send(cmd + "\n")
        time.sleep(2)  
        output = chan.recv(65535).decode(errors="ignore")
        print(output)
        if any( key in output for key in error_keywords):
            print("Error in command, discard and exiting...")
            chan.send( "discard\n")
            chan.send( "exit\n")
            break


    chan.close()
    client.close()
    
if __name__ == '__main__':
    cmd_list1 = ['show version | no-more',
                'configure',
                'set protocols ospf interface eth1 network point-to-point',
                'set protocols ospf parameters router-id 1.1.1.1',
                'set protocols ospf area 0 network 10.0.0.0/24',
                'set protocols ospf area 0 network 192.168.1.0/24',
                'set protocols ospf interface dum1 passive',
                'commit',
                'save',
                'exit'
                ]
    cmd_list2 = [
                'show ip ospf neighbor | no-more',
                'show ip ospf route | no-more'
    ]
    qyang_multicmd('172.17.9.216', 'vyos', 'vyos',cmd_list1)
    time.sleep(5)
    qyang_multicmd('172.17.9.216', 'vyos', 'vyos',cmd_list2)