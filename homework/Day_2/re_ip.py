import re

def get_info(string):
    pattern = re.compile(
        r'(?P<interface>Port-channel(?P<slot>\d+)\.(?P<number>\d+))\s+'
        r'(?P<ip>\d{1,3}(?:\.\d{1,3}){3})\s+'
        r'\S+\s+'                      # 跳过 YES/NO
        r'\S+\s+'                      # 跳过 CONFIG/STATIC
        r'(?P<status>UP|DOWN|ADMIN DOWN)'
    )
    match = pattern.match(string)
    if match:
        return match.groupdict()
    return None

if __name__ == "__main__":
    str1='Port-channel1.189     192.168.189.254 YES   CONFIG  UP'
    info = get_info(str1)
    fields = [
        ("接口", "interface"),
        ("IP地址", "ip"),
        ("状态", "status"),
    ]
    print('-'*80)
    for label, key in fields:
        print(f'{label:<10}：{info[key]}')