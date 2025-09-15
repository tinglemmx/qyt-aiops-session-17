from kamene.all import *  # Scapy 3.0+ Python 3.11 用 Kamene

# 配置参数
iface = "eth0"                 # 发送的网卡
my_ip = "192.168.76.200"       # 你要广播的 IP
my_mac = "00:11:22:33:44:55"   # 你自己的 MAC 地址

# 构造以太网帧（广播）
eth = Ether(dst="ff:ff:ff:ff:ff:ff", src=my_mac)

# 构造 ARP reply（Gratuitous ARP）
arp = ARP(op=2,               # 2 = reply
          hwsrc=my_mac,        # 本机 MAC
          psrc=my_ip,          # 本机 IP
          hwdst="ff:ff:ff:ff:ff:ff",  # 广播
          pdst=my_ip)          # IP 发给自己（Gratuitous）

# 组合并发送
pkt = eth / arp
sendp(pkt, iface=iface, verbose=True)
