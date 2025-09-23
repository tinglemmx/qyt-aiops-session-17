from sqlalchemy import Column, Integer, Float, String, DateTime, create_engine, BigInteger
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime
import pprint
from pathlib import Path
from qyt_libs.qytang_snmp import QytangSNMP
from influxdb import InfluxDBClient


pp = pprint.PrettyPrinter(indent=4)


base_dir = Path(__file__).resolve().parent
base_dir.mkdir(parents=True, exist_ok=True)
db_path = base_dir / 'db' / "interface_info.db"


# -----------------------
# 数据库模型定义
# -----------------------
Base = declarative_base()


class InterfaceData(Base):
    __tablename__ = 'router_monitor'

    id = Column(Integer, primary_key=True)
    record_datetime = Column(
        DateTime,
        default=lambda: datetime.now(datetime.timezone.utc),   # 默认存 UTC
        onupdate=lambda: datetime.now(datetime.timezone.utc)   # 更新时存 UTC
    )
    device_ip = Column(String(64), nullable=False)
    interface_name = Column(String(64), nullable=False)
    in_bytes = Column(BigInteger, nullable=False)
    out_bytes = Column(BigInteger, nullable=False)


# -----------------------
# 创建数据库
# -----------------------
engine = create_engine(
    f'sqlite:///{str(db_path)}?check_same_thread=False', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()


def get_interface_info_by_snmp(host, snmp_community, snmp_port=161, interface_list=None):

    record_body = []
    my_snmp = QytangSNMP(host, snmp_community)
    if_name_list = my_snmp.getSubtree(['IF-MIB', 'ifName'])
    rx_bytes = my_snmp.getSubtree(['IF-MIB', 'ifHCInOctets'])
    tx_bytes = my_snmp.getSubtree(['IF-MIB', 'ifHCOutOctets'])
    # print("if_name_list:")
    # pp.pprint(if_name_list)
    # print("rx_bytes:")
    # pp.pprint(rx_bytes)
    # print("tx_bytes:")
    # pp.pprint(tx_bytes)

    current_time = datetime.datetime.now(datetime.UTC).isoformat("T")
    for index, name in enumerate(if_name_list):
        fields = {}
        if interface_list and name[1] in interface_list:
            fields['rx_bytes'] = int(rx_bytes[index][1])
            fields['tx_bytes'] = int(tx_bytes[index][1])

            record_body.append(
                {
                    "measurement": "router_monitor",
                    "time": current_time,
                    "tags": {
                        "device_ip": host,
                        "device_type": "VYOS",
                        "interface_name": name[1]
                    },
                    "fields": fields,
                }
            )
            print(f"{host} ----> 接口信息采集结果:")
            pp.pprint(record_body)

    return record_body


def write_influxdb(influx_host, influx_user, influx_password, influx_db, data, influx_port=8086):
    if data:
        client = InfluxDBClient(
            influx_host, influx_port, influx_user, influx_password, influx_db)
        success = client.write_points(data)
        print(f"{router_ip} 采集信息写入influx数据库成功:{success}")
    else:
        print(f"{router_ip} fields为空跳过写入influx数据库")


def write_sqlite(data):
    for item in data:
        if item and item.get("fields"):
            tmp_data = InterfaceData(
                record_datetime=datetime.datetime.fromisoformat(item['time']),
                device_ip=item['tags']['device_ip'],
                interface_name=item['tags']['interface_name'],
                in_bytes=item['fields']['rx_bytes'],
                out_bytes=item['fields']['tx_bytes'],
            )
            session.add(tmp_data)
            session.commit()
            print(
                f"{router_ip} 采集信息写入sqlite数据库成功:{item['tags']['device_ip']}-{item['tags']['interface_name']}")
        else:
            print(f"{router_ip} fields为空跳过写入sqlite数据库")


if __name__ == "__main__":
    hosts = [
        {"host": "172.17.9.216", "snmp_community": "cisco@123",
            'interface_list': ['eth0', 'eth1']},
        {"host": "172.17.9.217", "snmp_community": "cisco@123",
            'interface_list': ['eth0', 'eth1']}
    ]
    influx_host = '172.17.9.210'
    influx_db = "qytdb"
    influx_port = 8086
    influx_measurement = "router_monitor"
    influx_user = "qytdbuser"
    influx_password = "Cisc0123"
    for host in hosts:
        router_ip = host['host']
        data = get_interface_info_by_snmp(
            router_ip, host['snmp_community'], interface_list=host['interface_list'])
        write_influxdb(influx_host, influx_user, influx_password,
                       influx_db, data, influx_port)
        try:
            write_sqlite(data)
        finally:
            session.close()
