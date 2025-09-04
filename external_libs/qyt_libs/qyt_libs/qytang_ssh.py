import paramiko

def qytang_ssh(ip, user, passwd, port=22, cmd='ls -1'):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=port, username=user, password=passwd,
                       timeout=5, compress=True)
        stdin, stdout, stderr = client.exec_command(cmd)
        result = stdout.read().decode()
        return result.strip() + '\n\n'
    finally:
        client.close()
