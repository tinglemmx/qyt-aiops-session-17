#!/usr/bin/env python
import traceback
import lxml.etree as et
from ncclient import manager
from ncclient.operations import RPCError
from typing import Optional


class CiscoNetconf:
    def __init__(self, host: str, username: str, password: str, port: int = 830, device_type: str = 'csr'):
        """
        初始化 Cisco 设备 NETCONF 会话参数
        :param host: 设备 IP 或域名
        :param username: 用户名
        :param password: 密码
        :param port: NETCONF 端口
        :param device_type: 设备类型，如 'csr' 或 'c9k'
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.device_type = device_type

    def _connect(self):
        """创建 NETCONF 会话"""
        return manager.connect(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            timeout=90,
            hostkey_verify=False,
            device_params={'name': self.device_type}
        )

    def _send_rpc(self, rpc_xml: str) -> Optional[str]:
        """发送 RPC 并返回 XML 字符串"""
        try:
            with self._connect() as m:
                response = m.dispatch(et.fromstring(rpc_xml))
                data = response.xml
                if et.iselement(data):
                    data = et.tostring(data, pretty_print=True).decode()
                return data
        except RPCError as e:
            return e.xml
        except Exception:
            traceback.print_exc()
            return None

    # ---------------- CPU 查询 ----------------
    def get_cpu_usage(self, monitor_type: str = "5s") -> int:
        CPU_MONITOR_TYPE = {
            "5s": "<five-seconds/>",
            "1m": "<one-minute/>",
            "5m": "<five-minutes/>"
        }
        if monitor_type not in CPU_MONITOR_TYPE:
            raise ValueError("Invalid monitor_type. Choose from '5s', '1m', '5m'.")
        else:
            monitor_type = CPU_MONITOR_TYPE[monitor_type]
        rpc = f'''
        <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <filter>
            <cpu-usage xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper">
              <cpu-utilization>
                {monitor_type}
              </cpu-utilization>
            </cpu-usage>
          </filter>
        </get>
        '''
        data = self._send_rpc(rpc)
        xml_data = et.tostring(et.fromstring(data.encode('utf-8')), pretty_print=True).decode()
        print(xml_data)
        if not xml_data:
            return -1
        return self._parse_cpu_value(xml_data)

    @staticmethod
    def _parse_cpu_value(xml_data: str) -> int:
        """解析 CPU 利用率"""
        try:
            root = et.fromstring(xml_data.encode("utf-8"))
            val = root.xpath(
                "//*[local-name()='five-seconds' or local-name()='one-minute' or local-name()='five-minutes']/text()"
            )
            if val:
                return int(val[0])
        except Exception:
            pass
        return -1

    # ---------------- Syslog 配置 ----------------
    def conf_syslog(self, severity: int, hostip: str) -> bool:
        """
        配置 syslog trap
        :param severity: 日志等级 0~7
        :param hostip: 远程 syslog 服务器 IP
        :return: True 成功, False 失败
        """
        rpc = f'''
        <edit-config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <target><running/></target>
          <config>
            <native xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-native">
              <logging>
                <trap>
                  <severity xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="create">{severity}</severity>
                </trap>
                <hostip xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="create">{hostip}</hostip>
              </logging>
            </native>
          </config>
        </edit-config>
        '''
        result = self._send_rpc(rpc)
        result_data = et.tostring(et.fromstring(result.encode('utf-8')), pretty_print=True).decode() if result else None
        print(result_data)
        return result is not None

if __name__ == "__main__":
    device = CiscoNetconf(host="192.0.2.210", username="admin", password="cisco1234")

    # 获取 CPU
    cpu_5s = device.get_cpu_usage("5s")
    print(f"5 秒 CPU 利用率: {cpu_5s}%")

    # 配置 syslog
    if device.conf_syslog(severity=7, hostip="10.1.1.60"):
        print("Syslog 配置成功")
    else:
        print("Syslog 配置失败")

