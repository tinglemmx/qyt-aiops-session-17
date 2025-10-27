
import copy
from genie.conf.base.utils import QDict
import json
import difflib
from deepdiff import DeepDiff
import jsondiff

def normalize_routes(routes_dict):
    """
    递归标准化路由表：
    - QDict 转成普通 dict
    - 所有 key 转成字符串
    - 过滤掉 updated 等不重要字段
    """
    def _clean(d):
        if isinstance(d, QDict):
            d = dict(d)  # QDict -> dict

        if isinstance(d, dict):
            new_d = {}
            for k, v in d.items():
                if k == "updated":  # 忽略 updated 字段
                    continue
                new_d[str(k)] = _clean(v)  # key 转字符串
            return new_d
        elif isinstance(d, list):
            return [_clean(v) for v in d]
        else:
            return d

    return _clean(copy.deepcopy(routes_dict))

def diff_routes_git_style(old, new, context=1):
    """
    显示老路由和新路由的差异，类似 git diff 风格
    :param old: 老路由 dict
    :param new: 新路由 dict
    :param context: 上下文条数
    """
    old_routes = normalize_routes(old)['vrf']['default']['address_family']['ipv4']['routes']
    new_routes = normalize_routes(new)['vrf']['default']['address_family']['ipv4']['routes']

    all_keys = sorted(set(old_routes.keys()) | set(new_routes.keys()))

    for idx, key in enumerate(all_keys):
        old_val = old_routes.get(key)
        new_val = new_routes.get(key)

        if old_val != new_val:
            # 上下文前
            for i in range(max(0, idx-context), idx):
                k = all_keys[i]
                print(f"  {k}: {new_routes.get(k, old_routes.get(k))}")

            # 差异部分
            if old_val is not None:
                print(f"- {key}: {old_val}")
            if new_val is not None:
                print(f"+ {key}: {new_val}")

            # 上下文后
            for i in range(idx+1, min(len(all_keys), idx+1+context)):
                k = all_keys[i]
                print(f"  {k}: {new_routes.get(k, old_routes.get(k))}")

            print("="*60)
            
old_routes_norm = {'vrf': {'default': {'address_family': {'ipv4': {'routes': {'0.0.0.0/0': {'route': '0.0.0.0/0', 'active': True, 'metric': 0, 'route_preference': 1, 'source_protocol_codes': 'S*', 'source_protocol': 'static', 'next_hop': {'next_hop_list': {'1': {'index': 1, 'next_hop': '172.17.9.1'}}}}, '1.1.100.1/32': {'route': '1.1.100.1/32', 'active': True, 'metric': 2, 'route_preference': 110, 'source_protocol_codes': 'O', 'source_protocol': 'ospf', 'next_hop': {'next_hop_list': {'1': {'index': 1, 'next_hop': '10.0.12.1', 'outgoing_interface': 'GigabitEthernet2'}}}}, '2.2.2.2/32': {'route': '2.2.2.2/32', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'Loopback0': {'outgoing_interface': 'Loopback0'}}}}, '2.2.100.0/24': {'route': '2.2.100.0/24', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'Loopback1': {'outgoing_interface': 'Loopback1'}}}}, '2.2.100.2/32': {'route': '2.2.100.2/32', 'active': True, 'source_protocol_codes': 'L', 'source_protocol': 'local', 'next_hop': {'outgoing_interface': {'Loopback1': {'outgoing_interface': 'Loopback1'}}}}, '10.0.12.0/30': {'route': '10.0.12.0/30', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'GigabitEthernet2': {'outgoing_interface': 'GigabitEthernet2'}}}}, '10.0.12.2/32': {'route': '10.0.12.2/32', 'active': True, 'source_protocol_codes': 'L', 'source_protocol': 'local', 'next_hop': {'outgoing_interface': {'GigabitEthernet2': {'outgoing_interface': 'GigabitEthernet2'}}}}, '172.17.9.0/24': {'route': '172.17.9.0/24', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'GigabitEthernet1': {'outgoing_interface': 'GigabitEthernet1'}}}}, '172.17.9.216/32': {'route': '172.17.9.216/32', 'active': True, 'source_protocol_codes': 'L', 'source_protocol': 'local', 'next_hop': {'outgoing_interface': {'GigabitEthernet1': {'outgoing_interface': 'GigabitEthernet1'}}}}}}}}}}
new_routes_norm = {'vrf': {'default': {'address_family': {'ipv4': {'routes': {'1.0.0.0/0': {'route': '0.0.0.0/0', 'active': True, 'metric': 0, 'route_preference': 1, 'source_protocol_codes': 'S*', 'source_protocol': 'static', 'next_hop': {'next_hop_list': {1: {'index': 1, 'next_hop': '172.17.9.1'}}}}, '1.1.100.1/32': {'route': '1.1.100.1/32', 'active': True, 'metric': 2, 'route_preference': 110, 'source_protocol_codes': 'O', 'source_protocol': 'ospf', 'next_hop': {'next_hop_list': {1: {'index': 1, 'next_hop': '10.0.12.1', 'outgoing_interface': 'GigabitEthernet2'}}}}, '2.2.2.2/32': {'route': '2.2.2.2/32', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'Loopback0': {'outgoing_interface': 'Loopback0'}}}}, '2.2.100.0/24': {'route': '2.2.100.0/24', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'Loopback1': {'outgoing_interface': 'Loopback1'}}}}, '2.2.100.2/32': {'route': '2.2.100.2/32', 'active': True, 'source_protocol_codes': 'L', 'source_protocol': 'local', 'next_hop': {'outgoing_interface': {'Loopback1': {'outgoing_interface': 'Loopback1'}}}}, '10.0.12.0/30': {'route': '10.0.12.0/30', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'GigabitEthernet2': {'outgoing_interface': 'GigabitEthernet2'}}}}, '10.0.12.2/32': {'route': '10.0.12.2/32', 'active': True, 'source_protocol_codes': 'L', 'source_protocol': 'local', 'next_hop': {'outgoing_interface': {'GigabitEthernet2': {'outgoing_interface': 'GigabitEthernet2'}}}}, '172.17.9.0/24': {'route': '172.17.9.0/24', 'active': True, 'source_protocol_codes': 'C', 'source_protocol': 'connected', 'next_hop': {'outgoing_interface': {'GigabitEthernet1': {'outgoing_interface': 'GigabitEthernet1'}}}}, '172.17.9.216/32': {'route': '172.17.9.216/32', 'active': True, 'source_protocol_codes': 'L', 'source_protocol': 'local', 'next_hop': {'outgoing_interface': {'GigabitEthernet1': {'outgoing_interface': 'GigabitEthernet1'}}}}}}}}}}        
old_str = json.dumps(normalize_routes(old_routes_norm), indent=2, sort_keys=True)
new_str = json.dumps(normalize_routes(new_routes_norm), indent=2, sort_keys=True)
# diff = difflib.unified_diff(
#     old_str.splitlines(),
#     new_str.splitlines(),
#     fromfile='old_routes',
#     tofile='new_routes',
#     lineterm='',
#     n=9999
# )

# print("\n".join(diff))

# diff = DeepDiff(old_routes_norm, new_routes_norm, ignore_order=True, verbose_level=2)
# print(json.dumps(diff, indent=2, ensure_ascii=False))

diff = jsondiff.diff(old_str, new_str)
print(json.dumps(diff, indent=2, ensure_ascii=False))
