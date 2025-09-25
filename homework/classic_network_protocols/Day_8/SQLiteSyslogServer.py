#!/usr/bin/env python3
import socket
import signal
import sys
import datetime
import re
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


base_dir = Path(__file__).resolve().parent
db_dir = base_dir / "db"
Path.mkdir(db_dir, exist_ok=True)
db_path = db_dir / "syslog.db"

# ----------------- 数据库配置 -----------------
DB_URL = f"sqlite:///{db_path}"
Base = declarative_base()

class Log(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, nullable=False)
    host = Column(String, nullable=False)
    facility = Column(Integer, nullable=False)
    severity = Column(Integer, nullable=False)
    severity_name = Column(String, nullable=False)
    message = Column(String, nullable=False)

engine = create_engine(DB_URL, echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
# ---------------------------------------------

# Severity 映射
severity_map = {
    0: "EMERG",
    1: "ALERT",
    2: "CRIT",
    3: "ERR",
    4: "WARNING",
    5: "NOTICE",
    6: "INFO",
    7: "DEBUG",
}

# ----------------- Syslog 服务器 -----------------
HOST = "0.0.0.0"
PORT = 514

running = True
def handle_sigint(sig, frame):
    global running
    print("\n[INFO] 收到退出信号，正在关闭...")
    running = False
def parse_pri(msg):

    match = re.match(r"<(\d+)>", msg)
    if match:
        pri = int(match.group(1))
        severity = pri % 8
        facility = pri // 8
        return facility, severity, severity_map.get(severity, "UNKNOWN")
    return None, None, None

def run_server():
    '''
    遵循 RFC 3164（传统 BSD Syslog） 
    <PRI>TIMESTAMP HOSTNAME TAG: MESSAGE
    <34>Oct 11 22:14:15 myhost myapp[1234]: test syslog message
    <34> = PRI = facility*8 + severity
        Oct 11 22:14:15 = 时间戳（无年份）
        myhost = 主机名
        myapp[1234] = 程序名和 PID
        test syslog message = 内容
        
    todo:
        FC 5424（更现代的标准格式）
        <PRI>1 TIMESTAMP HOSTNAME APP-NAME PROCID MSGID [STRUCTURED-DATA] MSG
        <34>1 2025-09-25T01:45:00Z myhost myapp 1234 ID47 [exampleSDID@32473 iut="3"] Test syslog message


    '''
    global running
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"Syslog server listening on {HOST}:{PORT},control+c to exit")

    session = Session()

    while running:
        try:
            sock.settimeout(1.0)  # 防止 recvfrom 永远阻塞
            data, addr = sock.recvfrom(4096)
            msg = data.decode(errors="replace").strip()
            facility, severity, sev_name = parse_pri(msg)
            if severity is None:
                continue

            log = Log(
                ts=datetime.datetime.now(datetime.timezone.utc),
                host=addr[0],
                facility=facility,
                severity=severity,
                severity_name=sev_name,
                message=msg
            )
            session.add(log)
            session.commit()
            print(f"[{log.ts}] {log.host} {log.severity_name}: {log.message}")
        except socket.timeout:
            continue
        except Exception as e:
            print(f"[ERROR] {e}")
    session.close()
    sock.close()
    print("[INFO] 已退出。")

if __name__ == "__main__":
    # SIGINT 即使ctrl + c 触发的
    signal.signal(signal.SIGINT, handle_sigint)
    run_server()
