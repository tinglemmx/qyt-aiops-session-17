import pyshark
from pathlib import Path
from datetime import timezone, datetime
import pprint
from elasticsearch import Elasticsearch, helpers


pp = pprint.PrettyPrinter(indent=4)

BASE_DIR = Path(__file__).resolve().parent
PCAP_FILE = BASE_DIR / "testxxx.pcap"


es = Elasticsearch("http://172.17.9.210:9200")



def print_pkt(cap):
    for pkt in cap:
        print(pkt)  # 简单打印包概要
        print(pkt.layers)  # 每一层
        for layer in pkt.layers:
            for field in layer.field_names:
                print(layer.get_field(field))

def packet_to_dict(pkt):
    ts = float(pkt.sniff_timestamp)
    iso_ts = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()
    pkt_dict = {"frame_number": int(pkt.number), 
                "timestamp": iso_ts }
    for layer in pkt.layers:
        layer_name = layer.layer_name
        pkt_dict[layer_name] = {}
        for field in layer.field_names:
            if not field:  # 忽略空字段名
                continue
            try:
                value = layer.get_field(field)
                pkt_dict[layer_name][field] = value
            except Exception:
                continue
    return pkt_dict


def write_to_es(packets):
    index_name = "qyt-pyshark-index"

    # 建索引（可选：定义 mapping）
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name)

    # 批量导入
    actions = [
        {
            "_index": index_name,
            "_source": pkt
        }
        for pkt in packets
    ]

    helpers.bulk(es, actions)
    print(f"已导入 {len(actions)} 个包到 Elasticsearch")


if __name__ == '__main__':
    packets = []
    # 读取 pcap 文件
    cap = pyshark.FileCapture(PCAP_FILE, keep_packets=False)
    for pkt in cap:
        packets.append(packet_to_dict(pkt))
    write_to_es(packets)