import subprocess
import time

TOTAL_LEN = 70

class QYTPING:
    def __init__(self, ip, size = 100, timeout=2,interval = 1):
        self.dstip = ip
        self.length = size
        self.timeout = timeout
        self.count = 5
        self.srcip = ''
        self.interval = interval
    
    def __repr__(self):
        class_name = self.__class__.__name__
        srcip_string = f"srcip: {self.srcip}, " if self.srcip else ''
        return f"<{class_name} => {srcip_string}dstip: {self.dstip}, size: {self.length}>"  
    
    def denerate_cmd(self):
        cmd_list = []
        if self.srcip:
            cmd_list.append(f"-I {self.srcip}")
        if self.length:
            cmd_list.append(f"-s {self.length}")
        if self.timeout:
            cmd_list.append(f"-W {self.timeout}")
        if self.count>0 and isinstance(self.count,int):
            cmd_list.append(f"-c 1")
        else:
            raise ValueError("connect must be a positive integer")
        cmd_list.append(self.dstip)
        return "ping " + " ".join(cmd_list)    

    def ping_one_packet(self,cmd):
        return_code, stdout, stderr = run_cmd(cmd)
        if return_code == 0:
            return True
        elif return_code == 1:
            return False
        else:
            raise Exception(f"Error: {return_code} -- {stderr}")
    
    def cisco_like_ping_result(self,result:bool):
        if result:
            return "!"
        else:
            return "."
    
    def ping(self):
        cmd = self.denerate_cmd()
        for i in range(self.count):
            result = self.ping_one_packet(cmd)
            print(self.cisco_like_ping_result(result), end="", flush=True)
            time.sleep(self.interval)
        print()

    def one(self):
        cmd = self.denerate_cmd()
        result = self.ping_one_packet(cmd)
        if result:
            print(f"{self.dstip} 可达！")
        else:
            print(f"{self.dstip} 不可达！")

class NewPing(QYTPING):
    def __init__(self, ip, size = 100, timeout=2):
        super().__init__(ip, size, timeout)

    def new_style_ping_result(self,result:bool):
        if result:
            return "+"
        else:
            return "?"
        
    def ping(self):
        cmd = self.denerate_cmd()
        for i in range(self.count):
            result = self.ping_one_packet(cmd)
            print(self.new_style_ping_result(result), end="", flush=True)
            time.sleep(self.interval)
        print()

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


def print_new(word,s='-'):
    global TOTAL_LEN
    s_len = int((TOTAL_LEN-len(word))/2)
    print(s*s_len+word+s*s_len)
    
    
if __name__ == "__main__":
    ping = QYTPING('223.5.5.5')
    print_new("print class")
    print(ping)
    print_new("print one for sure reachable")
    ping.one()
    print_new("ping five")
    ping.ping()
    print_new("set payload lenth")
    ping.length = 200
    print(ping)
    ping.ping()
    print_new("set ping src ip address")
    ping.srcip = '192.168.1.123'
    print(ping)
    ping.ping()
    print_new("new class NewPing","=")
    newping = NewPing('223.5.5.5')
    newping.length = 300
    print(newping)
    newping.ping()
