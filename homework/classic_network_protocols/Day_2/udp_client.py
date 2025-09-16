import socket
import struct
import hashlib
import pickle

def udp_send_data(ip, port, data_list):
    address = (ip, port)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    version = 1
    pkt_type = 1
    seq_id = 1
    # | 2B version | 2B type | 4B seq_id | 8B data_len | N bytes data | 16B md5 |
    for x in data_list:
        # ---变长数据部分---
        data = pickle.dumps(x)
        # ---头部---
        # H=2字节 ushort, I=4字节 uint, Q=8字节 uint64
        header = struct.pack("!HHIQ", version, pkt_type, seq_id, len(data))

        # ---计算校验---
        md5_val = hashlib.md5(header + data).digest()  # 16字节
        # ---拼接完整包---
        packet = header + data + md5_val
        # 限制总长度 512
        if len(packet) > 512:
            raise ValueError(f"数据包超长 {len(packet)} > 512")
        s.sendto(packet, address)
        seq_id += 1
    s.close()

if __name__ == '__main__':
    from datetime import datetime
    user_data = ['乾颐堂',[1,'qytang',3],{'qyang':1,'test':3},{'datetime':datetime.now()}]
    udp_send_data('172.17.9.210',6666,user_data)
        