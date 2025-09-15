import subprocess
import time

def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=isinstance(cmd, str), 
            capture_output=True,
            text=True
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return -1, "", str(e)

def get_netstat_tcp_port_list(string):
    port_list = []
    for line in string.split("\n"):
        if line.startswith("tcp") and "LISTEN" in line.strip():
            port_list.append(line.split()[3].split(":")[-1])
    return port_list
    
def check_http_service(port=80,interval=1):
    while True:
        return_code, stdout, stderr = run_cmd("netstat -tln")
        if return_code == 0:
            port_list = get_netstat_tcp_port_list(stdout)
            if str(port) in port_list:
                print(f"HTTP (TCP/{port}) 服务已经被打开")
                break
            else:
                print(f"等待一秒重新开始监控：")
        time.sleep(interval)  
    
if __name__ == "__main__":
    check_http_service()