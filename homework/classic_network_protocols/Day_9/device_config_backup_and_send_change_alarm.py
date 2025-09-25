import hashlib
import datetime
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, Session, declarative_base
from netmiko import ConnectHandler
import difflib

from qyt_libs.send_email import send_report

engine = create_engine(
    'postgresql+psycopg2://qytangdbuser:Cisc0123@172.17.9.210/qytangdb')

Base = declarative_base()


class Router(Base):
    __tablename__ = 'router'

    id = Column(Integer, primary_key=True)
    router_name = Column(String(64), nullable=False, index=True)
    ip = Column(String(64), nullable=False, index=True)
    username = Column(String(64), nullable=False)
    password = Column(String(64), nullable=False)

    # ----------接口------------
    interface = relationship(
        'Interface', back_populates="router", passive_deletes=True)

    # ----------OSPF------------
    # uselist=False表示onetoone
    ospf_process = relationship(
        'OSPFProcess', back_populates="router", uselist=False, passive_deletes=True)

    # --------CPU利用率----------
    cpu_usage = relationship(
        'CPUUsage', back_populates="router", passive_deletes=True)

    # --------设备配置-----------
    device_config = relationship(
        'DeviceConfig', back_populates="router", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.router_name})"


class DeviceConfig(Base):
    __tablename__ = 'device_config'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey(
        "router.id", ondelete='CASCADE'), nullable=False)
    device_config = Column(String(99999), nullable=False)
    config_md5 = Column(String(100), nullable=False)
    router = relationship(
        'Router', back_populates="device_config", passive_deletes=True)
    record_time = Column(DateTime(timezone='Asia/Chongqing'),
                         default=datetime.datetime.now)

    def __repr__(self):
        return f"{self.__class__.__name__}(Device IP: {self.router.ip} " \
               f"| Datetime: {self.record_time} " \
               f"| Config MD5: {self.config_md5})"


class Interface(Base):
    __tablename__ = 'interface'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey(
        "router.id", ondelete='CASCADE'), nullable=False)
    interface_name = Column(String(64), nullable=False)
    ip = Column(String(64), nullable=False)
    mask = Column(String(64), nullable=False)
    router = relationship(
        'Router', back_populates="interface", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.router.router_name} "\
               f"| Interface_name: {self.interface_name} " \
               f"| IP: {self.ip} / {self.mask})"


class OSPFProcess(Base):
    __tablename__ = 'ospf_process'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey(
        "router.id", ondelete='CASCADE'), nullable=False)
    processid = Column(Integer, nullable=False)
    routerid = Column(String(64), nullable=False)
    router = relationship(
        'Router', back_populates="ospf_process", passive_deletes=True)
    area = relationship(
        'Area', back_populates="ospf_process", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.router.router_name} " \
               f"| Process: {self.processid})"


class Area(Base):
    __tablename__ = 'area'

    id = Column(Integer, primary_key=True)
    ospfprocess_id = Column(Integer, ForeignKey(
        "ospf_process.id", ondelete='CASCADE'), nullable=False)
    area_id = Column(Integer, nullable=False)
    ospf_process = relationship(
        'OSPFProcess', back_populates="area", passive_deletes=True)
    ospf_network = relationship(
        'OSPFNetwork', back_populates="area", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.ospf_process.router.router_name} " \
               f"| Process: {self.ospf_process.processid} " \
               f"| Area: {self.area_id})"


class OSPFNetwork(Base):
    __tablename__ = 'ospf_network'

    id = Column(Integer, primary_key=True)
    area_id = Column(Integer, ForeignKey(
        "area.id", ondelete='CASCADE'), nullable=False)
    network = Column(String(64), nullable=False)
    wildmask = Column(String(64), nullable=False)
    area = relationship(
        'Area', back_populates="ospf_network", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.area.ospf_process.router.router_name} " \
               f"| Process: {self.area.ospf_process.processid} " \
               f"| Area: {self.area.area_id} " \
               f"| Network: {self.network}/{self.wildmask})"


class CPUUsage(Base):
    __tablename__ = 'cpu_usage'

    id = Column(Integer, primary_key=True)
    router_id = Column(Integer, ForeignKey(
        "router.id", ondelete='CASCADE'), nullable=False)
    cpu_useage_percent = Column(Integer, nullable=False)
    cpu_useage_datetime = Column(
        DateTime(timezone='Asia/Chongqing'), default=datetime.datetime.now)
    router = relationship(
        'Router', back_populates="cpu_usage", passive_deletes=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(Router: {self.router.router_name} " \
               f"| Datetime: {self.cpu_useage_datetime} " \
               f"| Percent: {self.cpu_useage_percent})"


# 连接数据库的会话
SessionLocal = sessionmaker(bind=engine)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
Path.mkdir(TEMPLATES_DIR, exist_ok=True)


def fetch_config_for_vyos(router: Router):
    device = {
        "device_type": "vyos",
        "host": router.ip,
        "username": router.username,
        "password": router.password,
    }
    conn = ConnectHandler(**device)
    config = conn.send_command("show configuration commands | no-more")
    conn.disconnect()
    return config


def save_device_config(session: Session, router: Router, config: str):
    try:
        # 计算 MD5
        import hashlib
        md5sum = hashlib.md5(config.encode("utf-8")).hexdigest()

        # 创建 DeviceConfig 实例
        device_config = DeviceConfig(
            router=router,
            device_config=config,
            config_md5=md5sum,
            record_time=datetime.datetime.now(datetime.timezone.utc)
        )

        # 添加到 session
        session.add(device_config)
        # 提交事务
        session.commit()
        dt = router.device_config[-1].record_time
        local_dt = dt.astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")

        print(f"{router.router_name} 配置保存成功{local_dt}")
        return device_config

    except Exception as e:
        session.rollback()  # 回滚当前事务，不影响其他设备
        print(f"{router.router_name} 配置保存失败: {e}")
        return None


def check_config_change(session: Session, router: Router):
    last_two = session.query(DeviceConfig)\
                      .filter_by(router_id=router.id)\
                      .order_by(DeviceConfig.id.desc())\
                      .limit(2)\
                      .all()

    if len(last_two) < 2:
        # 不足两条，不做对比
        return False
    old_config = last_two[1].device_config
    new_config = last_two[0].device_config
    router_info = f"{router.router_name}({router.ip})"
    if last_two[0].config_md5 != last_two[1].config_md5:
        print(f"{router_info} 配置有变化,发送邮件")
        diff_report = generate_config_diff_email(
            old_config,
            new_config,
            router_info
        )
        return True
    else:
        print(f"{router_info} 配置没有变化")

    return False


def generate_config_diff_email(old_config: str, new_config: str, router_name: str):
    diff = difflib.unified_diff(
        old_config.splitlines(),
        new_config.splitlines(),
        fromfile='old_config',
        tofile='new_config',
        n=max(len(old_config.splitlines()), len(new_config.splitlines())),
        lineterm=''
    )
    diff_text = '\n'.join(diff)
    # 邮件正文
    email_body = f"""\
    设备: {router_name}
    
    ==== 配置差异 ====
    {diff_text}
    
    """
    diff_html = f"<pre>{diff_text}</pre>"

    send_report(
        subject=f"设备{router_name},配置异常,具体配置看正文",
        sender="********@qq.com",
        recipients=["********@hotmail.com"],
        html_content=diff_html,
        image_files={},
        smtp_host="smtp.qq.com",
        smtp_port=587,
        username="********@qq.com",
        password="********"
    )


if __name__ == "__main__":
    router_list = []
    with SessionLocal() as session:
        router_ids = [r.id for r in session.query(Router.id).all()]

    for router_id in router_ids:
        try:
            # 每个设备一个独立 session
            with SessionLocal() as session:
                router = session.get(Router, router_id)
                if router is None:
                    print(f"Router {router_id} 不存在")
                    continue
                # 拉配置
                config = fetch_config_for_vyos(router)
                # 保存配置
                save_device_config(session, router, config)
                check_config_change(session, router)

        except Exception as e:
            print(f"设备 {router.router_name} 处理失败: {e}")
            # 可以记录日志或报警
            continue
