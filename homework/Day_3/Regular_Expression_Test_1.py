import re

def get_mac_address_info(string):
    fields = [
        ("VLAN ID", "vlan_id"),
        ("MAC", "mac_address"),
        ("Type", "type"),
        ("Interface", "interface"),
    ]
    pattern = re.compile(
        r'^(?P<vlan_id>\S+)\s+'   # 不止id 还会有字符串 ’All‘
        r'(?P<mac_address>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+'
        r'(?P<type>\S+)\s+' 
        r'(?P<interface>\S+)$'
    )
    match = pattern.match(string)
    if match:
        return match.groupdict(),fields
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
    test_string = '166 54a2.74f7.0326 DYNAMIC Gi1/0/11'
    print_info(*get_mac_address_info(test_string))
