from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship, sessionmaker,declarative_base
from sqlalchemy import Index,UniqueConstraint
from datetime import datetime,timezone
from collections.abc import Iterable
from sqlalchemy.dialects.postgresql import JSONB


from enum import Enum
from sqlalchemy import Enum as SQLEnum

class ProtocolEnum(Enum):
    snmp = "snmp"
    gnmi = "gnmi"
    restconf = "restconf"
    telemetry = "telemetry"

# 创建SQLAlchemy基础模型
Base = declarative_base()

# 数据库连接配置
engine = create_engine('postgresql://myuser:mypass@127.0.0.1:5432/mydb')
Session = sessionmaker(bind=engine)

class Vendor(Base):
    """厂商，例如 Cisco, Juniper, Arista"""
    __tablename__ = 'devices_vendor'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(String)

    def __str__(self):
        return self.name


class DeviceType(Base):
    """设备类型，例如 Cisco Router, Juniper Switch 等"""
    __tablename__ = 'devices_devicetype'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    vendor_id = Column(Integer, ForeignKey('devices_vendor.id'))
    description = Column(String)
    
    vendor = relationship('Vendor', backref='device_types')

    def __str__(self):
        return f"{self.vendor.name}_{self.name}"


class DeviceDB(Base):
    """设备基本信息"""
    __tablename__ = 'devices_devicedb'
    id = Column(Integer, primary_key=True)
    hostname = Column(String(100), unique=True)
    ip_address = Column(String(45))  # Use String for IP (IPv4/IPv6)
    description = Column(String)
    dev_type_id = Column(Integer, ForeignKey('devices_devicetype.id'))
    snmp_ro_community = Column(String(100), default='public')
    snmp_rw_community = Column(String(100), default='private')
    ssh_username = Column(String(100), nullable=True)
    ssh_password = Column(String(100), nullable=True)
    enable_password = Column(String(100), nullable=True)
    last_update = Column(DateTime, default=datetime.now(timezone.utc))

    dev_type = relationship('DeviceType', backref='devices')

    def __str__(self):
        return f"{self.hostname} ({self.ip_address} {self.snmp_ro_community})"


class MetricType(Base):
    """定义指标类型，可映射到不同的采集协议与路径"""
    __tablename__ = 'devices_metrictype'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    protocol = Column(SQLEnum(ProtocolEnum), default=ProtocolEnum.snmp)
    metric_path = Column(String(300))  # OID 或 gRPC Path
    description = Column(String)
    unit = Column(String(50), nullable=True)

    def __str__(self):
        return f"{self.name} [{self.protocol.value}:{self.metric_path}]"

class MetricMapping(Base):
    """定义逻辑指标与实际采集指标 (MetricType) 的关系"""
    __tablename__ = 'devices_metricmapping'
    id = Column(Integer, primary_key=True)
    logical_name = Column(String(100))
    metric_type_id = Column(Integer, ForeignKey('devices_metrictype.id'))
    device_type_id = Column(Integer, ForeignKey('devices_devicetype.id'))
    is_primary = Column(Boolean, default=True)
    metric_type = relationship('MetricType', backref='metric_mappings')
    device_type = relationship('DeviceType', backref='metric_mappings')
    
    __table_args__ = (
        UniqueConstraint('logical_name', 'metric_type_id', 'device_type_id', name='uq_logical_metric_device'),
        Index('ix_logical_name', 'logical_name'),
    )

    def __str__(self):
        return f"{self.logical_name}:{self.device_type} → {self.metric_type.protocol}:{self.metric_type.metric_path}"



class DeviceMetric(Base):
    """设备采集的实际指标数据"""
    __tablename__ = 'devices_devicemetric'
    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey('devices_devicedb.id'))
    metric_type_id = Column(Integer, ForeignKey('devices_metrictype.id'))
    timestamp = Column(DateTime, default=datetime.now(timezone.utc))
    metrics = Column(JSONB)  # JSON-like string for storing metric data
    success = Column(Boolean, default=True)

    device = relationship('DeviceDB', backref='metrics')
    metric_type = relationship('MetricType', backref='metrics')

    def __str__(self):
        return f"{self.device.hostname} @ {self.timestamp.isoformat()} ({self.metric_type.name})"


# 创建表
# Base.metadata.create_all(engine)


def  db_item_print(model_class):
    session = Session()

    for item in session.query(model_class).all():
        print(item)
    session.close()
    
def db_relationship_print(model_class,key):
    session = Session()


    for item in session.query(model_class).all():
        related_items = getattr(item, key, None)

        if related_items is None:
            print(f"{item} has no related items")
        elif isinstance(related_items, Iterable) and not isinstance(related_items, (str, bytes)):
            related_item_list = [str(ri) for ri in related_items]
            if related_item_list:
                print(f"{item} has related items:")
                for ri in related_item_list:
                    print(f" -- {ri}")
            else:
                print(f"{item} has no related items")
        else:
            # 不是可迭代对象，直接打印
            print(f"{item} has related item: {related_items}")
            
    session.close()

def integr_device_metric_type():
    session = Session()
    devices = session.query(DeviceDB).all()
    for dev in devices:
        print(dev)
        device_type = dev.dev_type
        # mappings = session.query(MetricMapping).filter_by(device_type_id=device_type.id).all()
        mappings = device_type.metric_mappings
        for mapping in mappings:
            print("    ",mapping.metric_type.protocol.value, "---" ,mapping.metric_type.metric_path)
    session.close()

if __name__ == "__main__":
    # 测试数据库连接和模型

    # db_item_print(Vendor)
    # db_relationship_print(Vendor, 'device_types')

    # db_item_print(DeviceType)
    # db_relationship_print(DeviceType, 'devices')
    # db_relationship_print(DeviceType, 'vendor')
    # db_relationship_print(DeviceType, 'metric_mappings')
    # db_relationship_print(DeviceType, 'metrics')
    
    # db_item_print(DeviceDB)
    
    # db_item_print(MetricType)

    # db_item_print(MetricMapping) 
    
    
    # db_item_print(DeviceMetric)
    # db_relationship_print(DeviceMetric, 'device')
    
    integr_device_metric_type()
    
