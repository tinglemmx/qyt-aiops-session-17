#!/usr/bin/env python3
import os
import django
from datetime import datetime, timezone
import asyncio
from pysnmp.hlapi.asyncio import getCmd, SnmpEngine, CommunityData, ContextData, UdpTransportTarget, ObjectType, ObjectIdentity

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from devices.models import DeviceMetric, MetricMapping

# --- 异步 SNMP GET ---
async def snmp_get(ip, community, oid, port=161, timeout=1, retries=3):
    snmpEngine = SnmpEngine()
    errorIndication, errorStatus, errorIndex, varBinds = await getCmd(
        snmpEngine,
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, port), timeout=timeout, retries=retries),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    if errorIndication:
        return False, {'value': None, 'error_msg': str(errorIndication)}
    elif errorStatus:
        msg = "{} at {}".format(
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or "?"
        )
        return False, {'value': None, 'error_msg': msg}
    else:
        result = [x.prettyPrint() for x in varBinds[0]]
        return True, {'value': result[1], 'error_msg': None}


# --- 同步采集主函数 ---
def collect_snmp_for_device(device):
    # ORM 查询放在同步上下文执行
    metric_mapping = list(
    MetricMapping.objects.select_related("metric_type").filter(
        device_type=device.dev_type,
        is_primary=True
        )
    )

    # 仅 SNMP 请求在异步中执行
    async def collect_all():
        tasks = []
        for mapping in metric_mapping:
            metric = mapping.metric_type
            if metric.protocol != 'snmp':
                continue
            coro = snmp_get(device.ip_address, device.snmp_ro_community, metric.metric_path)
            tasks.append((metric, coro))

        results = []
        for metric, coro in tasks:
            success, value = await coro
            results.append((metric, success, value))
        return results

    # === 正确运行异步任务 ===
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    results = loop.run_until_complete(collect_all())

    # ORM 写操作也在同步上下文中执行
    for metric, success, value in results:
        DeviceMetric.objects.create(
            device=device,
            metric_type=metric,
            timestamp=datetime.now(timezone.utc),
            metrics=value,
            success=success
        )
        print(f"{device.hostname} {metric.name}: {'OK' if success else 'FAIL'}")
