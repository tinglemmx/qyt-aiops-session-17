from kamene.layers.l2 import Ether, ARP
from kamene.sendrecv import sendp

def build_gratuitous_arp(my_ip, my_mac):
    eth = Ether(dst="ff:ff:ff:ff:ff:ff", src=my_mac)
    # 构造 ARP reply（Gratuitous ARP）
    arp = ARP(op=2,               # 2 = reply
            hwsrc=my_mac,        # 本机 MAC
            psrc=my_ip,          # 本机 IP
            hwdst="ff:ff:ff:ff:ff:ff",  # 广播
            pdst=my_ip)          # IP 发给自己（Gratuitous）

    return eth / arp
    
if __name__ == '__main__':
    iface = "ens160"   
    my_ip = "172.17.9.216" 
    my_mac = "00:50:56:a4:22:1a"
    pkt = build_gratuitous_arp(my_ip, my_mac)
    sendp(pkt, iface=iface, verbose=True)
