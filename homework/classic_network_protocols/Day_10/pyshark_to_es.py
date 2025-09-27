import pyshark
from datetime import timezone, timedelta, datetime
from elasticsearch import Elasticsearch
from pathlib import Path

# 设置时区为 UTC
tzutc_0 = timezone(timedelta(hours=0))

# 连接 Elasticsearch
es = Elasticsearch("http://172.17.9.210:9200")

# PCAP 文件路径
BASE_DIR = Path(__file__).resolve().parent
PCAP_FILE = BASE_DIR / "test.pcapng"

# PyShark 读取 PCAP 数据包
cap = pyshark.FileCapture(PCAP_FILE, keep_packets=False)  # 不保存包到内存，节省内存

def packet_to_dict(pkt):
    """把 PyShark 包对象转换为可写入 Elasticsearch 的字典"""
    pkt_dict_final = {}

    # 时间戳
    ts = float(pkt.sniff_timestamp)
    pkt_dict_final['sniff_time'] = datetime.fromtimestamp(ts, tz=tzutc_0).isoformat(timespec='milliseconds') + 'Z'

    # 层级信息
    pkt_dict_final['highest_layer'] = pkt.highest_layer

    # 遍历所有层
    for layer in pkt.layers:
        layer_name = layer.layer_name
        pkt_dict_final[layer_name] = {}
        for field in layer.field_names:
            if not field:
                continue
            try:
                value = layer.get_field(field)
                # 尝试把数字字段转成 int
                if field in ('len', 'ip_len', 'ttl', 'id', 'sport', 'dport'):
                    try:
                        value = int(value)
                    except Exception:
                        pass
                pkt_dict_final[layer_name][field.replace('.', '_')] = value
            except Exception:
                continue

    return pkt_dict_final

def write_pkt_es(pkt):
    """写入单个包到 Elasticsearch"""
    try:
        pkt_dict = packet_to_dict(pkt)
        # 使用包的 sniff_timestamp 生成每日索引
        ts = datetime.fromtimestamp(float(pkt.sniff_timestamp), tz=tzutc_0)
        index_name = f"qyt-pyshark-{ts.strftime('%Y.%m.%d')}"
        resp = es.index(index=index_name, document=pkt_dict)
        print(f"Packet {pkt.number} indexed: {resp['result']}")
    except Exception as e:
        print(f"Failed to index packet {pkt.number}: {e}")

# 批量处理 PCAP
cap.apply_on_packets(write_pkt_es)
