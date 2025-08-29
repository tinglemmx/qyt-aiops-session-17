import re

def firewall_info_to_dict(string):
    asa_dict = {}
    for line in string.split('\n'):
        pattern = re.compile(
            r'^(?P<proto>\S+)\s+'                  # 协议
            r'(?P<src_if>\S+)\s+'                  # 源接口
            r'(?P<src_ip>\d+\.\d+\.\d+\.\d+):(?P<src_port>\d+)\s+'  # 源IP:端口
            r'(?P<dst_if>\S+)\s+'                  # 目的接口
            r'(?P<dst_ip>\d+\.\d+\.\d+\.\d+):(?P<dst_port>\d+),\s+' # 目的IP:端口
            r'idle\s+(?P<idle>\d+:\d+:\d+),\s+'    # idle 时间
            r'bytes\s+(?P<bytes>\d+),\s+'          # 字节数
            r'flags\s+(?P<flags>\S+)'              # flags
        )
        match = pattern.match(line.strip())
        if match:
            asa_dict[(
                      match.group('src_ip'), 
                      match.group('src_port'),
                      match.group('dst_ip'), 
                      match.group('dst_port')
                )] = (
                      match.group('bytes'), 
                      match.group('flags')
                     )
    return asa_dict
                
def format_print(asa_dict):
    print("格式化打印输出")
    src = 'src'
    src_port = 'src_port'
    dst = 'dst'
    dst_port = 'src_port'
    bytes_name = 'bytes'
    flags = 'flags'
    
    format_str1 = [src,src_port,dst,dst_port]
    format_str2 = [bytes_name,flags]
    
    for key, value in asa_dict.items():
        print('|'.join( f"{format_str1[i]:^10}:{key[i]:^15}" for i in range(len(format_str1))))
        print('|'.join( f"{format_str2[i]:^10}:{value[i]:^15}" for i in range(len(format_str2))))
        print('='*(26*4+3))

if __name__ == '__main__':
    asa_conn = "TCP Student 192.168.189.167:32806 Teacher 137.78.5.128:65247, idle 0:00:00, bytes 74, flags UIO\n TCP Student 192.168.189.167:80 Teacher 137.78.5.128:65233, idle 0:00:03, bytes 334516, flags UIO"
    conn_info_dict = firewall_info_to_dict(asa_conn)
    print(conn_info_dict,'\n')
    format_print(conn_info_dict)