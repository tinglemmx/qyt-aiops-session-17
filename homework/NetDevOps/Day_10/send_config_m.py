from pyats.topology import loader
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# 日志配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

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

def push_config(name, device, cfg):
    try:
        logging.info(f"{name}: 正在连接...")
        device.connect()
        logging.info(f"{name}: 连接成功，开始下发配置")
        device.configure(cfg)
        logging.info(f"{name}: 配置完成")
        device.disconnect()
        return f"{name}: success"
    except Exception as e:
        logging.error(f"{name}: 配置失败: {e}")
        return f"{name}: failed"

def main():
    with ThreadPoolExecutor(max_workers=len(testbed.devices)) as executor:
        futures = []
        for name, device in testbed.devices.items():
            cfg = ospf_configs.get(name)
            if cfg:
                futures.append(executor.submit(push_config, name, device, cfg))
        for future in as_completed(futures):
            logging.info(future.result())

if __name__ == "__main__":
    main()
