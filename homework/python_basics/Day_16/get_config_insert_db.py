from datetime import datetime,timezone,timedelta
from sqlalchemy import create_engine, Column, Integer, String, DateTime,Text
from sqlalchemy.orm import declarative_base, sessionmaker,Session
from pathlib import Path
import hashlib
import time

from qyt_libs import qytang_ssh


# 定义数据库连接（SQLite）
base_dir = Path(__file__).parent.resolve()
db_file = base_dir / "db" / "sqlalchemy_sqlite3.db"
db_file.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(
    f"sqlite:///{db_file}?check_same_thread=False", 
    echo=False  # echo=True 会打印SQL语句，调试方便
    ) 
Base = declarative_base() # 得到一个 ORM 基类
SessionLocal  = sessionmaker(bind=engine)

# 定义表模型
class DeviceConfig(Base):
    __tablename__ = "device_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    config_data = Column(Text)
    config_hash = Column(String, index=True) 
    recorded_time = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),   # 默认存 UTC
        onupdate=lambda: datetime.now(timezone.utc)   # 更新时存 UTC
    )

    def __repr__(self):
        return f"{self.__class__.__name__}(id：{self.id}| Config Hash：{self.config_hash}| "\
               f"Recorded Time: {self.recorded_time})"

def save_device_config(session: Session, config_data: str,config_hash:str):
    # 插入新配置
    new_config = DeviceConfig(
        config_data=config_data,
        config_hash=config_hash
    )
    session.add(new_config)
    session.commit()
def get_last_config_hash(session: Session):
    last_config_hash = session.query(DeviceConfig).order_by(DeviceConfig.id.desc()).first()
    return last_config_hash.config_hash if last_config_hash else None

def qytang_get_config(ip, username, password,port=22):
    result = qytang_ssh(ip, username, password, port, 'vbash -ic "show configuration commands | no-more"')
    result_lit = result.split('\n')
    index = next((i for i, s in enumerate(result_lit) if "set system host-name" in s), -1)
    return '\n'.join(result_lit[index:])

def run_config_backup(ip,username, password,port=22):
    # 获取最后保存的配置hash
    with SessionLocal() as session_check:
        last_config_hash_before_save = get_last_config_hash(session_check)
    # 获取配置
    current_config = qytang_get_config(ip, username, password, port)
    # 计算MD5
    hash_obj = hashlib.sha256()
    hash_obj.update(current_config.encode('utf-8'))
    current_config_md5 = hash_obj.hexdigest()
    # 保存配置 到数据库
    with SessionLocal() as session_insert:
        save_device_config(session_insert,current_config,current_config_md5)
    # 获取最后保存的配置hash
    with SessionLocal() as session_check:
        last_config_hash_after_save = get_last_config_hash(session_check)
    print(f"本次采集的HASH：{last_config_hash_after_save}")
    if last_config_hash_before_save != last_config_hash_after_save:
        print(f"{'='*10}配置发生变化{'='*10}")
        print(f"{' '*4}{'THE MOST RECENT HASH':<24}:{last_config_hash_after_save}")
        print(f"{' '*4}{'THE LAST HASH':<24}:{last_config_hash_before_save}")
        
def main():
    Base.metadata.create_all(engine, checkfirst=True)
    try:
        while True:
            run_config_backup('172.17.9.216', 'vyos', 'vyos')
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n检测到 Ctrl-C，程序退出")

if __name__ == "__main__":
    main()