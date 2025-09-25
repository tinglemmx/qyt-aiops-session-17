#!/usr/bin/env python3
import socket
import datetime
import platform

class Facility:
    KERN, USER, MAIL, DAEMON, AUTH, SYSLOG, LPR, NEWS, UUCP, CRON, AUTHPRIV, FTP = range(12)
    LOCAL0, LOCAL1, LOCAL2, LOCAL3, LOCAL4, LOCAL5, LOCAL6, LOCAL7 = range(16, 24)

class Level:
    EMERG, ALERT, CRIT, ERR, WARNING, NOTICE, INFO, DEBUG = range(8)

class SyslogClient:
    """Modern Syslog client (RFC3164) over UDP"""
    def __init__(self, host="localhost", port=514, facility=Facility.LOCAL7):
        self.host = host
        self.port = port
        self.facility = facility
        self.hostname = platform.node()
        self.appname = "myapp"
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _format_message(self, message: str, level: int) -> str:
        """Format message according to RFC3164"""
        pri = self.facility * 8 + level
        timestamp = datetime.datetime.now().strftime("%b %d %H:%M:%S")
        return f"<{pri}>{timestamp} {self.hostname} {self.appname}: {message}"

    def send(self, message: str, level: int):
        """Send a syslog message with a specified severity"""
        logmsg = self._format_message(message, level)
        self.socket.sendto(logmsg.encode(), (self.host, self.port))

    # Convenience methods for common levels
    def warning(self, message: str):
        self.send(message, Level.WARNING)

    def notice(self, message: str):
        self.send(message, Level.NOTICE)

    def error(self, message: str):
        self.send(message, Level.ERR)

    def info(self, message: str):
        self.send(message, Level.INFO)

    def debug(self, message: str):
        self.send(message, Level.DEBUG)

if __name__ == "__main__":
    client = SyslogClient("127.0.0.1")
    # 单条发送
    client.notice("This is a notice log")
    client.warning("This is a warning log")
    client.error("This is an error log")
    client.info("This is an info log")
    client.debug("This is a debug log")
