import socket
from datetime import datetime
import pytz
from pathlib import Path
import psutil
from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

base_dir = Path(__file__).resolve().parent

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
    cpu_percent = Column(Float)    # CPU 平均利用率 %
    mem_total = Column(Float)      # 内存总量 MB
    mem_used = Column(Float)       # 内存已用 MB
    mem_free = Column(Float)       # 内存空闲 MB
    mem_percent = Column(Float)    # 内存使用率 %

# -----------------------
# 创建数据库
# -----------------------
engine = create_engine(f'sqlite:///{str(base_dir)}/cpu_mem.db?check_same_thread=False', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

# -----------------------
# 数据采集函数
# -----------------------
def collect_and_save():
    mem = psutil.virtual_memory()
    mem_total = mem.total / 1024 / 1024
    mem_used  = mem.used / 1024 / 1024
    mem_free  = mem.free / 1024 / 1024
    mem_percent = mem.percent

    cpu_percents = psutil.cpu_percent(percpu=True)
    cpu_avg = sum(cpu_percents) / len(cpu_percents)  # 计算平均值

    timestamp = datetime.now(tz)  # 东八区时间
    
    device_ip = get_device_ip()

    
    data = CpuMemData(
        timestamp=timestamp,
        device_ip=device_ip,
        cpu_percent=cpu_avg,
        mem_total=mem_total,
        mem_used=mem_used,
        mem_free=mem_free,
        mem_percent=mem_percent
    )
    session.add(data)

    session.commit()
    print(f"{timestamp}: 保存 CPU {len(cpu_percents)} 核心 + 内存数据成功")

def get_device_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "127.0.0.1"
    return ip

# -----------------------
# 主循环（每隔 5 秒采集一次）
# -----------------------
if __name__ == "__main__":
    collect_and_save()
