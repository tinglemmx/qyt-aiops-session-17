import random
import ipaddress

def random_ipv4():
    # 生成 0~2^32-1 的随机整数
    addr_int = random.randint(0, 2**32 - 1)
    # 转换为 IPv4Address 对象
    return str(ipaddress.IPv4Address(addr_int))

if __name__ == '__main__':
    print(random_ipv4())