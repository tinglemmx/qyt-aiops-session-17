import pytz
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from write_db_ssh import CpuMemData  # 导入write_db_ssh定义的数据库模型
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib import dates, ticker
from matplotlib.ticker import MultipleLocator
from matplotlib.dates import AutoDateLocator, DateFormatter
from datetime import datetime, timedelta
from random import random, choice


# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False

# 基础路径
base_dir = Path(__file__).resolve().parent
db_path = base_dir / "cpu_mem.db"

# 数据库设置
Base = declarative_base()
engine = create_engine(
    f'sqlite:///{str(db_path)}?check_same_thread=False', echo=False)
Base.metadata.create_all(engine)
_Session = sessionmaker(bind=engine)
session = _Session()

# 时区设置
tz = pytz.timezone("Asia/Shanghai")  # 东八区


def get_last_timestamp(session: Session):
    last_timestamp_row = session.query(CpuMemData.timestamp).order_by(
        CpuMemData.timestamp.desc()).first()
    return last_timestamp_row[0]


def get_hosts_list(session: Session):
    devices_list = [row[0] for row in session.query(
        CpuMemData.device_ip).distinct().all()]
    return devices_list


def get_mem_and_cpu_usage_list(session: Session, device_ip: str, last_timestamp):
    timestamp_list = []
    mem_usage_list = []
    cpu_total_list = []
    cpu_idle_w_iowait_list = []
    cpu_usage_list = []
    one_hour_ago = last_timestamp - \
        timedelta(hours=1) - timedelta(minutes=1) - timedelta(seconds=10)
    # 这里会最多拿到62条数据,1个小时应该有61个记录(包含两端点),多拿一个是为了算cpu的使用率
    results = session.query(CpuMemData.timestamp, CpuMemData.mem_percent, CpuMemData.cpu_total, CpuMemData.cpu_idle_w_iowait)\
        .filter(CpuMemData.device_ip == device_ip)\
        .filter(CpuMemData.timestamp >= one_hour_ago)\
        .order_by(CpuMemData.timestamp)\
        .all()

    if len(results) > 62:
        raise Exception(f"数据量({len(results)})大于62，请检查results数据！")

    for row in results:
        timestamp_list.append(row[0])
        mem_usage_list.append(row[1])
        cpu_total_list.append(row[2])
        cpu_idle_w_iowait_list.append(row[3])

    mem_usage_list.pop(0)
    timestamp_list.pop(0)
    cpu_usage_list = calculate_cpu_usage(
        cpu_total_list, cpu_idle_w_iowait_list)
    return timestamp_list, mem_usage_list, cpu_usage_list


def calculate_cpu_usage(cpu_total_list, cpu_idle_w_iowait_list):
    cpu_usage_list = []
    for i in range(1, len(cpu_total_list)):
        total_dalta = cpu_total_list[i] - cpu_total_list[i-1]
        idle_delata = cpu_idle_w_iowait_list[i] - cpu_idle_w_iowait_list[i-1]
        cpu_usage = (total_dalta - idle_delata) / total_dalta * 100
        cpu_usage_list.append(cpu_usage)
    return cpu_usage_list


def draw_line_chart(
    lines_list: list,
    x_label: str,
    y_label: str,
    title: str,
    file_name: str
):
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot(111)
    ax.xaxis.set_major_formatter(dates.DateFormatter("%H:%M"))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%3.1f%%"))
    ax.set_ylim(ymin=0, ymax=100)
    fig.autofmt_xdate()  # 自动旋转，避免重叠
    locator = AutoDateLocator(minticks=13, maxticks=20)  # 控制最少和最多显示的刻度数
    ax.xaxis.set_major_locator(locator)
    ax.yaxis.set_major_locator(MultipleLocator(10))  # 每10%一个刻度

    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    fig.autofmt_xdate()

    for x_list, y_list, line_style, line_name in lines_list:
        ax.plot(x_list, y_list, line_style, label=line_name)

    ax.legend(loc='upper left')

    # 保存图片
    plt.savefig(str(base_dir / file_name))


def generating_line_chart_per_device(session: Session, device_ip, last_timestamp):
    timestamp_list, mem_usage_list, cpu_usage_list = get_mem_and_cpu_usage_list(
        session, device_ip, last_timestamp)
    cpu_usage_info_list = [timestamp_list, cpu_usage_list, "-", device_ip]
    mem_usage_info_list = [timestamp_list, mem_usage_list, "--", device_ip]
    return cpu_usage_info_list, mem_usage_info_list


def generating_line_chart(session: Session):
    mhost_cpu_usage_info_list = []
    mhost_mem_usage_info_list = []
    last_timestamp = get_last_timestamp(session)
    devices_list = get_hosts_list(session)
    for device_ip in devices_list:
        cpu_usage_info_list, mem_usage_info_list = generating_line_chart_per_device(
            session, device_ip, last_timestamp)
        mhost_cpu_usage_info_list.append(cpu_usage_info_list)
        mhost_mem_usage_info_list.append(mem_usage_info_list)
    draw_line_chart(mhost_cpu_usage_info_list, '记录时间',
                    '百分比', "CPU利用率", "cpu_usage.png")
    draw_line_chart(mhost_mem_usage_info_list, '记录时间',
                    '百分比', "MEM利用率", "mem_usage.png")


if __name__ == '__main__':
    try:
        generating_line_chart(session)
    finally:
        session.close()
