from pyats.topology import loader
from datetime import datetime, timezone
import sqlite3
import json
import smtplib
from email.message import EmailMessage
from pathlib import Path
import copy
import logging
from genie.conf.base import Device
from genie.conf.base.utils import QDict
import difflib
from qyt_libs.send_email import send_report
from deepdiff import DeepDiff


# 抑制 INFO 及以下日志
logging.getLogger('unicon').setLevel(logging.WARNING)
logging.getLogger('genie').setLevel(logging.WARNING)
logging.getLogger('pyats').setLevel(logging.WARNING)

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / 'device_status.db'
TESTBED_FILE = BASE_DIR / 'testbed.yaml'

# -------------------------
# 数据库初始化（首次运行）
# -------------------------
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS device_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_name TEXT,
    device_ip TEXT,
    ospf_state TEXT,
    routes TEXT,
    timestamp_utc TEXT
)
''')
conn.commit()
conn.close()

# -------------------------
# 邮件通知
# -------------------------


def generate_config_diff_email(diff_text: str, router_name: str):

    email_body = f"""\
设备: {router_name}
    
==== 路由差异 ====

{diff_text}
    
    """
    email_html_body = f"<pre>{email_body}</pre>"

    send_report(
        subject=f"设备{router_name}路由表有变化",
        sender="*****@qq.com",
        recipients=["*****@hotmail.com"],
        html_content=email_html_body,
        image_files={},
        smtp_host="smtp.qq.com",
        smtp_port=587,
        username="*****@qq.com",
        password="*****"
    )

# -------------------------
# 过滤掉 updated 等无关字段
# -------------------------

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



# -------------------------
# 采集函数
# -------------------------


def collect_device(device):
    device.connect(timeout=60, learn_hostname=True)
    name = device.name
    ip = device.connections.cli.ip

    # 获取 OSPF 状态
    ospf_state = device.parse('show ip ospf neighbor')

    # 获取路由表
    routes = device.parse('show ip route')

    device.disconnect()

    return {
        'name': name,
        'ip': str(ip),
        'ospf_state': ospf_state,
        'routes': routes,
        'timestamp': datetime.now(timezone.utc)
    }


# -------------------------
# 单线程采集所有设备
# -------------------------
testbed = loader.load(TESTBED_FILE)
device_data_list = []

for dev_name, dev in testbed.devices.items():
    try:
        data = collect_device(dev)
        device_data_list.append(data)
        print(f"[{data['name']}] 采集成功")
    except Exception as e:
        print(f"[{dev_name}] 采集失败: {e}")

# -------------------------
# 一次性写入数据库 & 路由变化检测
# -------------------------
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

for data in device_data_list:
    # 检查最新一条记录的路由
    c.execute(
        'SELECT routes FROM device_info WHERE device_name=? ORDER BY id DESC LIMIT 1', (data['name'],))
    row = c.fetchone()
    if row:
        try:
            old_routes = json.loads(row[0])
        except Exception:
            old_routes = row[0]  # 如果不是 json，直接用原值

        old_routes_norm = normalize_routes(old_routes)
        new_routes_norm = normalize_routes(data['routes'])

        old_str = json.dumps(old_routes_norm, indent=2, sort_keys=True)
        new_str = json.dumps(new_routes_norm, indent=2, sort_keys=True)
        if old_str != new_str:
            # diff = difflib.unified_diff(
            #     old_str.splitlines(),
            #     new_str.splitlines(),
            #     fromfile='old_routes',
            #     tofile='new_routes',
            #     lineterm='',
            #     n=9999
            # )
            # diff_text = "\n".join(diff)
            # generate_config_diff_email(diff_text,data['name'])
            diff = DeepDiff(old_routes_norm, new_routes_norm, ignore_order=True, verbose_level=2)
            diff_text = json.dumps(diff, indent=2, ensure_ascii=False)
            generate_config_diff_email(diff_text,data['name'])

    # 插入新记录
    c.execute('''
        INSERT INTO device_info 
        (device_name, device_ip, ospf_state, routes, timestamp_utc) 
        VALUES (?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['ip'],
        json.dumps(data['ospf_state']),
        json.dumps(data['routes']),
        data['timestamp'].isoformat()
    ))

conn.commit()
conn.close()
print("所有设备状态已采集并存入数据库。")
