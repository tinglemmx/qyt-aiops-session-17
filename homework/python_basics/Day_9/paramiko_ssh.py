import paramiko

def qytang_ssh(ip, user, passwd, port=22, cmd='ls -1'):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=port, username=user, password=passwd,
                       timeout=5, compress=True)
        stdin, stdout, stderr = client.exec_command(cmd, get_pty=True)
        result = stdout.read().decode()
        return result.strip() + '\n\n'
    finally:
        client.close()


if __name__ == '__main__':
    print(qytang_ssh('172.17.9.215', 'vyos', 'Cisco@1234', 22))
    print(qytang_ssh('172.17.9.215', 'vyos', 'Cisco@1234', 22, cmd='pwd'))
    