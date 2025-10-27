from pyats.topology import loader
from pathlib import Path
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout  # 只打印到控制台，不写文件
)
BASE_DIR = Path(__file__).resolve().parent

testbed = loader.load(BASE_DIR / 'testbed.yaml')

ospf_configs = {
    'csr1': """
hostname CSR1
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
interface Loopback1
 ip address 1.1.100.1 255.255.255.0
interface GigabitEthernet2
 ip address 10.0.12.1 255.255.255.252
 no shut
router ospf 1
 router-id 1.1.1.1
 network 10.0.12.0 0.0.0.3 area 0
 network 1.1.100.0 0.0.0.255 area 0
""",
    'csr2': """
hostname CSR2
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
interface Loopback1
 ip address 2.2.100.2 255.255.255.0
interface GigabitEthernet2
 ip address 10.0.12.2 255.255.255.252
 no shut
router ospf 1
 router-id 2.2.2.2
 network 10.0.12.0 0.0.0.3 area 0
 network 2.2.100.0 0.0.0.255 area 0
"""
}

for name, device in testbed.devices.items():
    device.connect()
    print(f"正在为 {name} 下发配置 ...")
    device.configure(ospf_configs[name])
    device.disconnect()

print("两台设备 OSPF 配置完成。")
