import paramiko
import argparse
def qytang_ssh(ip, user, passwd, port=22, cmd='ls'):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=port, username=user, password=passwd,
                       timeout=5, compress=True)
        stdin, stdout, stderr = client.exec_command(cmd)
        stdout.channel.recv_exit_status()
        result = stdout.read().decode()
        return result.strip() + '\n\n'
    finally:
        client.close()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage='python Simple_SSH_Client -i ipaddr -u username -p password -c command')
    
    parser.add_argument('-i', '--ipaddr', help='SSH Server', required=True)
    parser.add_argument('-u', '--username', help='SSH Username', default='vyos')
    parser.add_argument('-p', '--password', help='SSH Password', default='vyos')
    parser.add_argument('-c', '--command', help='Shell Command', default='ls')

    args = parser.parse_args()

    output = qytang_ssh(args.ipaddr, args.username, args.password, cmd=args.command)
    print(output)