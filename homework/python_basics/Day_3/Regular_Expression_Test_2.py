import re

def format_idle_time(idle_str: str) -> str:
    parts = idle_str.split(":")
    if len(parts) != 3:
        return idle_str 
    hours, minutes, seconds = parts
    return f"{str(hours):<2}小时 {str(minutes):<2}分钟 {str(seconds):<2}秒"
def get_conn(string):
    items = ["protocol", "server", "localserver", "idle", "bytes", "flags"]
    fields = [ (k,k) for k in items ]
    pattern = re.compile(
        r'^(?P<protocol>\S+)\s+'
        r'server\s+(?P<server>\d{1,3}(?:\.\d{1,3}){3}:\d+)\s+'
        r'localserver\s+(?P<localserver>\d{1,3}(?:\.\d{1,3}){3}:\d+),\s+'
        r'idle\s+(?P<idle>\S+),\s+'
        r'bytes\s+(?P<bytes>\d+),\s+'
        r'flags\s+(?P<flags>\S+)$'
    )
    match = pattern.match(string)
    if match:
        info = dict(match.groupdict())
        if info.get('idle'):
            info['idle'] = format_idle_time(info['idle'])
        return info,fields
    return None,fields

def print_info(info,fields=None):
    if fields == None:
        raise ValueError('fields is None')
    max_len = max(len(x[0]) for x in fields)
    field_width = max_len + 5
    if info:
        for label, key in fields:
            print(f'{label:<{field_width}}: {info.get(key,"N/A")}')
    else:
        print('No match')

if __name__ == "__main__":
    test_string = 'TCP server 172.16.1.101:443 localserver 172.16.66.1:53710, idle 0:01:09, bytes 27575949, flags UIO'
    print_info(*get_conn(test_string))
