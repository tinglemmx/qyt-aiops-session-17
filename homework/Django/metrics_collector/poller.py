from snmp_client import snmp_get
from database_models import Session, DeviceDB, DeviceMetric
from datetime import datetime, timezone
import json
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)
def poll_snmp_for_all_devices():
    session = Session()
    devices = session.query(DeviceDB).all()

    for dev in devices:
        print(f"\n=== {dev.hostname} / {dev.ip_address} / {dev.snmp_ro_community} ===")

        mappings = dev.dev_type.metric_mappings   # 该设备类型对应的所有指标

        for mapping in mappings:
            mt = mapping.metric_type

            # 只采 SNMP 的
            if mt.protocol.value != "snmp":
                continue

            oid = mt.metric_path
            value = snmp_get(dev.ip_address, dev.snmp_ro_community, oid)

            print(f"  OID={oid}  VALUE={value}")

            #写入数据库
            record = DeviceMetric(
                device_id=dev.id,
                metric_type_id=mt.id,
                timestamp=datetime.now(timezone.utc),
                metrics=value[1],
                success=value[0]
            )


            session.add(record)

    session.commit()
    session.close()


if __name__ == "__main__":
    while True:
        try:
            print(f"=== Polling at {datetime.now().isoformat()} ===")
            poll_snmp_for_all_devices()
        except Exception as e:
            print(f"Error during polling: {e}")
        time.sleep(10)