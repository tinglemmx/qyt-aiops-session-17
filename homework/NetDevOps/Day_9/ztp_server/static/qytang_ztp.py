# This script is intended to run on Cisco IOS-XE/C8000v devices that have embedded Python and 'cli' available.
# It will:
#  - read hypervisor info and UUID via CLI
#  - POST {uuid, model} to ZTP server
#  - get rendered config and apply via cli.configurep
INVENTORY = """NAME: "Chassis", DESCR: "Cisco CSR1000V Chassis"
PID: CSR1000V          , VID: V00  , SN: 9FMY5L02HIN

NAME: "module R0", DESCR: "Cisco CSR1000V Route Processor"
PID: CSR1000V          , VID: V00  , SN: JAB1303001C

NAME: "module F0", DESCR: "Cisco CSR1000V Embedded Services Processor"
PID: CSR1000V          , VID:      , SN:      """
SYSTEM_HYPERVISOR = """Hypervisor: KVM
Manufacturer: QEMU
Product Name: Standard PC (i440FX + PIIX, 1996)
Serial Number: Not Specified
UUID: C97E58D9-974B-4EDB-A3F9-25B63DBA2B9A
image_variant :
"""

try:
    import cli # type: ignore # Cisco 内置模块
except ImportError:
    class cli:
        @staticmethod
        def cli(cmd):
            print(f"[MOCK] run cli: {cmd}")
            if cmd == "show inventory":
                return INVENTORY
            elif cmd == "show platform software system hypervisor":
                return SYSTEM_HYPERVISOR
            return ""
        @staticmethod
        def configurep(cmds):
            print("[MOCK] applying config:")
            for c in cmds:
                print("  ", c)
try:
    import requests
    import re
    from typing import Optional, Dict
    import json
    import time
except Exception as e:
    # On non-device environment, just exit
    print("This script is for device execution (needs cli module).", e)
    raise SystemExit(1)

ZTP_SERVER = "http://172.17.9.210:8000"
GET_CONFIG_URL = f"{ZTP_SERVER}/ztp/get_config"

def get_device_identity():
    """返回 {model, serial, uuid}"""
    identity = {"model": None, "serial": None, "uuid": None}

    try:
        inv = cli.cli("show inventory")
        identity.update(parse_show_inventory(inv))
    except Exception:
        pass
    
    try:
        hyper = cli.cli("show platform software system hypervisor")
        for line in hyper.splitlines():
            if "UUID:" in line:
                identity["uuid"] = line.split("UUID:")[1].strip()
    except Exception:
        pass

    return identity
def apply_config_text(config_text):
    # split lines and feed to configurep
    commands = [ln.strip() for ln in config_text.splitlines() if ln.strip()]
    print("Applying config:")
    for c in commands:
        print(c)
    cli.configurep(commands)
    # save
    cli.cli("write memory")

def parse_show_inventory(output: str) -> Optional[Dict[str, str]]:
    """
    解析 Cisco 'show inventory' 输出，提取每个模块的 PID/VID/SN

    :param output: show inventory 命令的完整输出字符串
    :return: 包含每个模块的字典列表，每个字典含 pid/vid/sn
    """
    lines = output.splitlines()
    chassis_index = None
    # 找到 NAME: "Chassis" 的行
    for i, line in enumerate(lines):
        if 'NAME: "Chassis"' in line:
            chassis_index = i
            break

    if chassis_index is None or chassis_index + 1 >= len(lines):
        return None
    
    # 下一行是Chassis PID/VID/SN
    pid_line = lines[chassis_index + 1]
    
    pattern = re.compile(
        r"PID:\s*(?P<pid>\S+)\s*,\s*VID:\s*(?P<vid>\S*)\s*,\s*SN:\s*(?P<sn>\S*)"
    )

    match = pattern.search(pid_line)
    if match:
        return {
            "model": match.group("pid"),
            "serial": match.group("sn")
        }

    return None

def main():
    identity = get_device_identity()
    uuid, model = identity["uuid"], identity["model"]
    if not uuid:
        print("UUID not found via CLI, abort.")
        return

    payload = {"uuid": uuid, "model": model}
    try:
        resp = requests.post(GET_CONFIG_URL, json=payload, timeout=10)
        data = resp.json()
    except Exception as e:
        print("Failed to contact server:", e)
        return

    if data.get("status") != "ok":
        print("Server returned error:", data)
        return

    config = data.get("config", "")
    if config:
        apply_config_text(config)
    else:
        print("Empty config returned")
        

if __name__ == "__main__":
    main()
