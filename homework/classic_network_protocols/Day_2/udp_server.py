import socket
import struct
import pickle
import hashlib
import sys

def udp_receive_data(ip, port, buffer_size=512):
    """
    UDP 接收端，解析自定义协议数据。
    """
    print('UDP服务就绪!等待客户数据!')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip, port))

    while True:
        packet, addr = s.recvfrom(buffer_size)

        if len(packet) < 32:  # 头部(16B) + MD5(16B) = 32B
            print("包太短，丢弃")
            continue

        # ---拆头部---
        header = packet[:16]  # 2+2+4+8 = 16B
        version, pkt_type, seq_id, data_len = struct.unpack("!HHIQ", header)

        # ---拆数据部分---
        data_end = 16 + data_len
        data = packet[16:data_end]
        md5_recv = packet[data_end:data_end+16]

        # ---校验长度---
        if len(data) != data_len:
            print(f"数据长度不符，期望 {data_len} 实际 {len(data)}")
            continue

        # ---校验 MD5---
        md5_calc = hashlib.md5(header + data).digest()
        if md5_calc == md5_recv:
            print('='*80)
            print(f"{'数据源自于':<30}:{str(addr):<30}")
            print(f"{'数据序列号':<30}:{seq_id:<30}")
            print(f"{'数据长度为':<30}:{data_len:<30}")
            print(f"{'数据内容为':<30}:{str(pickle.loads(data)):<30}")
        else:
            print('MD5校验错误！')

def run_server(ip, port, buffer_size=512):
    try:
        udp_receive_data(ip, port, buffer_size)
    except KeyboardInterrupt:
        print('\n退出程序！')
        sys.exit()
        
if __name__ == "__main__":
    run_server("0.0.0.0", 6666)
