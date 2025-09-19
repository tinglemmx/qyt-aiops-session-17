import socket
from datetime import datetime
import pytz
from pathlib import Path
import psutil
from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from qyt_libs import qytang_ssh

base_dir = Path(__file__).resolve().parent
# base_dir = Path.home() / "cpu_monitor"
base_dir.mkdir(parents=True, exist_ok=True)
db_path = base_dir / "cpu_mem.db"
# -----------------------
# 时区设置
# -----------------------
tz = pytz.timezone("Asia/Shanghai")  # 东八区

# -----------------------
# 数据库模型定义
# -----------------------
Base = declarative_base()

class CpuMemData(Base):
    __tablename__ = 'router_monitor'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(tz))  # 默认东八区时间
    device_ip = Column(String(64))
    mem_percent = Column(Float)    # 内存利用率 %
    cpu_total = Column(Float)      # CPU 总消耗时间
    cpu_idle_w_iowait = Column(Float)  # CPU idle + iowait

# -----------------------
# 创建数据库
# -----------------------
engine = create_engine(f'sqlite:///{str(db_path)}?check_same_thread=False', echo=False)
Base.metadata.create_all(engine)
_Session = sessionmaker(bind=engine)
session = _Session()

# -----------------------
# 数据采集函数
# -----------------------
def collect_and_save_by_ssh(host, username, password,port=22):
    mem_info = qytang_ssh(host, username, password, cmd = "cat /proc/meminfo")
    mem_percent = get_mem_usage(mem_info)
    cpu_stat = qytang_ssh(host, username, password, cmd = "cat /proc/stat")
    cpu_total,cpu_idle_w_iowait = get_cpu_usage(cpu_stat)

    timestamp = datetime.now(tz)  # 东八区时间
    
    data = CpuMemData(
        timestamp=timestamp,
        device_ip=host,
        mem_percent=mem_percent,
        cpu_total=cpu_total,
        cpu_idle_w_iowait=cpu_idle_w_iowait,
    )
    session.add(data)

    session.commit()
    print(f"{timestamp}: 保存 CPU + 内存数据成功{str(base_dir / 'cpu_mem.db')}")

def get_mem_usage(data):
    mem_total = None    
    mem_available  = None 
    for line in data.split("\n"):
        if line.startswith("MemTotal"):
            mem_total = int(line.split()[1])
        elif line.startswith("MemAvailable"):
            mem_available = int(line.split()[1])
    mem_used = (mem_total - mem_available) / mem_total * 100
    return mem_used

def get_cpu_usage(data):
    cpu_total = None
    cpu_idle = None
    for line in data.split("\n"):
        if line.startswith("cpu "):
            print(line)
            cpu_list = line.split()
            cpu_total = sum(map(int, cpu_list[1:9]))
            cpu_idle = int(cpu_list[4])
            cpu_iowait = int(cpu_list[5])
            cpu_idle_w_iowait = cpu_idle + cpu_iowait
    return cpu_total,cpu_idle_w_iowait



if __name__ == "__main__":
    hosts = [
        {"host": "172.17.9.216", "username": "vyos", "password": "vyos"},
        {"host": "172.17.9.217", "username": "vyos", "password": "vyos"}
        ]
    try:
        for host in hosts:
            collect_and_save_by_ssh(**host)
    finally:
        session.close()
