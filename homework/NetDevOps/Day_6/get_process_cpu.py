#!/usr/bin/env python3
import traceback
import lxml.etree as et
from argparse import ArgumentParser
from ncclient import manager
from ncclient.operations import RPCError

CPU_MONITOR_TYPE = {
    "5s": "<five-seconds/>",
    "1m": "<one-minute/>",
    "5m": "<five-minutes/>"
}


def build_payload(monitor_type: str) -> str:
    """构造 NETCONF payload"""
    cpu_tag = CPU_MONITOR_TYPE.get(monitor_type, "<five-seconds/>")
    return f"""
    <get xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <filter>
        <cpu-usage xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-process-cpu-oper">
          <cpu-utilization>
            {cpu_tag}
          </cpu-utilization>
        </cpu-usage>
      </filter>
    </get>
    """


def parse_cpu_value(xml_data: str) -> int:
    """解析 XML 响应中的 CPU 利用率数值"""
    try:
        root = et.fromstring(xml_data.encode("utf-8"))
        val = root.xpath(
            "//*[local-name()='five-seconds' or local-name()='one-minute' or local-name()='five-minutes']/text()")
        if val:
            return int(val[0])
    except Exception:
        pass
    return -1


def get_cpu_usage(host: str, username: str, password: str, monitor_type: str, port: int = 830) -> int:
    """主函数：连接设备并获取 CPU 利用率"""
    payload = build_payload(monitor_type)

    try:
        with manager.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            timeout=60,
            hostkey_verify=False,
            device_params={'name': 'csr'}
        ) as m:
            try:
                response = m.dispatch(et.fromstring(payload))
                data = response.xml
            except RPCError as e:
                data = e.xml

            # 格式化
            xml_data = et.tostring(et.fromstring(
                data.encode('utf-8')), pretty_print=True).decode()
            cpu_val = parse_cpu_value(xml_data)

            print(xml_data)
            print(f"\nCPU usage ({monitor_type}): {cpu_val}%")
            return cpu_val

    except Exception as e:
        print("NETCONF Error:", e)
        traceback.print_exc()
        return -1


if __name__ == "__main__":
    host = "192.0.2.210"
    username = "admin"
    password = "cisco123"
    get_cpu_usage(host, username, password, "5s")
