
import time
import logging

logging.getLogger("kamene.runtime").setLevel(logging.ERROR)

from kamene.all import IP, ICMP, sr1

def build_icmp_packet(target, src_address=None, payload=b'A'):
    if src_address:
        ip_layer = IP(src=src_address, dst=target)
    else:
        ip_layer = IP(dst=target)
    
    pkt = ip_layer/ICMP()/payload
    return pkt
def qytang_ping(target: str,src_address = None, timeout: int = 2):
    pkt = build_icmp_packet(target, src_address)
    start_time = time.time()
    reply = sr1(pkt, timeout=timeout, verbose=0) 
    end_time = time.time()
    if reply:
        # print(reply.show(), end="\n\n")
        rtt = (end_time - start_time) * 1000 
        print(f"Ping {target} success, RTT = {rtt:.2f} ms")
        return True
    else:
        print(f"Ping {target} failed")
        return False

