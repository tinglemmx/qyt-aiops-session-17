#!/usr/bin/env python3
from scapy.all import IP, UDP, send
import datetime
from random import choice

# ------------------ 配置 ------------------
SERVER_IP = "127.0.0.1"   # syslog server
SERVER_PORT = 514
APPNAME = "myapp"

# 伪造多台设备的 IP
FAKE_HOSTS = ["10.0.0.1", "10.0.0.2", "192.168.1.100"]

# severity 映射
SEVERITY_MAP = {
    0: "EMERG", 1: "ALERT", 2: "CRIT", 3: "ERR",
    4: "WARNING", 5: "NOTICE", 6: "INFO", 7: "DEBUG"
}
FACILITY_MAP = {
    0: "kernel messages",
    1: "user-level messages",
    2: "mail system",
    3: "system daemons",
    4: "security/authorization messages",
    5: "messages generated internally by syslogd",
    6: "line printer subsystem",
    7: "network news subsystem",
    8: "UUCP subsystem",
    9: "clock daemon",
    10: "security/authorization messages (private)",
    11: "FTP daemon",
    12: "NTP subsystem",
    13: "log audit",
    14: "log alert",
    15: "clock daemon (note 2)",
    16: "local0",
    17: "local1",
    18: "local2",
    19: "local3",
    20: "local4",
    21: "local5",
    22: "local6",
    23: "local7",
}
# Facility 可以全部用 LOCAL7
# FACILITY = 23  # LOCAL7
# ------------------------------------------

def format_rfc3164(message: str, facility_code: int, severity: int, fake_host: str) -> str:
    """生成标准 RFC3164 日志"""
    
    pri = facility_code * 8 + severity
    timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
    return f"<{pri}>{timestamp} {fake_host} {APPNAME}: {message}"

def send_fake_syslog(message_count):
    """给单台伪造主机发送每个 severity 的日志"""
    for _ in range(message_count):
        fake_host = choice(FAKE_HOSTS)
        severity = choice(range(8))
        facility_code = choice(list(FACILITY_MAP.keys()))
        facility_name = FACILITY_MAP[facility_code]
        msg_text = f"Test log from {fake_host}, severity {SEVERITY_MAP[severity]}"
        logmsg = format_rfc3164(msg_text, facility_code, severity, fake_host)
        pkt = IP(src=fake_host, dst=SERVER_IP) / UDP(sport=12345, dport=SERVER_PORT) / logmsg
        send(pkt, verbose=0)
        print(f"Sent: {fake_host} {facility_name}:{SEVERITY_MAP[severity]} -> {SERVER_IP}")

if __name__ == "__main__":
    send_fake_syslog(100)
