import asyncio
import datetime
from qyt_libs import qytang_ssh
from influxdb import InfluxDBClient
from pysnmp.hlapi.v3arch.asyncio import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, get_cmd


def get_cpu_and_mem_info(host, username, password, port=22, snmp_port=161):
    fields = {}

    try:
        mem_info = qytang_ssh(host, username, password,
                              cmd="cat /proc/meminfo")
        mem_total, mem_available, mem_free = get_mem_usage(mem_info)
        fields["mem_total"] = mem_total
        fields["mem_available"] = mem_available
        fields["mem_free"] = mem_free
    except Exception as e:
        print(f"[get_cpu_and_mem_info] 获取内存信息失败: {e}")

    try:
        cpu_stat = qytang_ssh(host, username, password, cmd="cat /proc/stat")
        cpu_total, cpu_idle_w_iowait = get_cpu_usage(cpu_stat)
        fields["cpu_total"] = cpu_total
        fields["cpu_idle_w_iowait"] = cpu_idle_w_iowait
    except Exception as e:
        print(f"[get_cpu_and_mem_info] 获取CPU信息失败: {e}")

    try:
        cpu_load1 = asyncio.run(
            snmp_get(host, "cisco@123", ".1.3.6.1.4.1.2021.11.11.0"))
        if cpu_load1 and cpu_load1[0] is not None:
            fields["cpu_load1"] = 100 - float(cpu_load1[0])
        else:
            print(f"[get_cpu_and_mem_info] 获取SNMP信息失败 !")
    except Exception as e:
        print(f"[get_cpu_and_mem_info] 获取SNMP信息失败: {e}")

    current_time = datetime.datetime.now(datetime.UTC).isoformat("T")

    cpu_mem_body = [
        {
            "measurement": "router_monitor",
            "time": current_time,
            "tags": {
                "device_ip": host,
                "device_type": "VYOS"
            },
            "fields": fields,
        }
    ]

    return cpu_mem_body


def get_mem_usage(data):
    mem_total = None
    mem_available = None
    for line in data.split("\n"):
        if line.startswith("MemTotal"):
            mem_total = int(line.split()[1])
        elif line.startswith("MemAvailable"):
            mem_available = int(line.split()[1])
        elif line.startswith("MemFree:"):
            mem_free = int(line.split()[1])
    return mem_total, mem_available, mem_free


def get_cpu_usage(data):
    cpu_total = None
    cpu_idle = None
    for line in data.split("\n"):
        if line.startswith("cpu "):
            # print(line)
            cpu_list = line.split()
            cpu_total = sum(map(int, cpu_list[1:9]))
            cpu_idle = int(cpu_list[4])
            cpu_iowait = int(cpu_list[5])
            cpu_idle_w_iowait = cpu_idle + cpu_iowait
    return cpu_total, cpu_idle_w_iowait


async def snmp_get(ip, community, oid_dict, snmp_port=161):
    result = []
    snmpEngine = SnmpEngine()

    iterator = get_cmd(
        snmpEngine,
        CommunityData(community, mpModel=0),
        await UdpTransportTarget.create((ip, snmp_port)),
        ContextData(),
        # ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)), # SNMPv2-MIB::sysDescr.0 → 1.3.6.1.2.1.1.1.0
        ObjectType(ObjectIdentity(oid_dict))
    )

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print("[snmp_get]", errorIndication)

    elif errorStatus:
        print(
            "[snmp_get]{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:

            print("[snmp_get]", " = ".join([x.prettyPrint() for x in varBind]))
            result.append(varBind[1].prettyPrint())
    snmpEngine.close_dispatcher()
    return result


if __name__ == "__main__":
    hosts = [
        {"host": "172.17.9.216", "username": "vyos", "password": "vyos"},
        {"host": "172.17.9.217", "username": "vyos", "password": "vyos"}
    ]
    influx_host = '172.17.9.210'
    influx_db = "qytdb"
    influx_port = 8086
    influx_measurement = "router_monitor"
    influx_user = "qytdbuser"
    influx_password = "Cisc0123"
    for host in hosts:
        router_ip = host['host']
        data = get_cpu_and_mem_info(router_ip, "vyos", "vyos")
        if data[0].get("fields"):
            client = InfluxDBClient(
                influx_host, influx_port, influx_user, influx_password, influx_db)
            success = client.write_points(data)
            print(f"{router_ip} CPU和MEM写入数据库成功:{success}")
        else:
            print(f"{router_ip} fields为空跳过写入数据库")
