#!/usr/bin/python3

import json
import time

ZTP_SERVER = "http://172.17.9.210:8000"
GET_CONFIG_URL = f"{ZTP_SERVER}/ztp/get_config"
print("\n\n *** Sample ZTP Day0 Python Script *** \n\n")

try:
    import cli # type: ignore # Cisco 内置模块
except ImportError:
    class cli:
        @staticmethod
        def cli(cmd):
            print(f"[MOCK] run cli: {cmd}")
            return ""
        @staticmethod
        def configurep(cmds):
            print("[MOCK] applying config:")
            for c in cmds:
                print("  ", c)

# --------------------------
# HTTP POST using urllib
# --------------------------
try:
    import urllib.request
    import urllib.error
except ImportError:
    print("urllib not available, cannot fetch remote config.")
    raise SystemExit(1)

def post_json(url, data):
    """POST JSON to server and return parsed JSON response"""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print("Failed to contact server:", e)
        return None

# --------------------------
# Device identity
# --------------------------
def parse_show_inventory(output):
    import re
    pattern = re.compile(r"PID:\s*(?P<pid>\S+)\s*,\s*VID:\s*(?P<vid>\S*)\s*,\s*SN:\s*(?P<sn>\S*)")
    match = pattern.search(output)
    if match:
        return {"model": match.group("pid"), "serial": match.group("sn")}
    return {"model": None, "serial": None}

def get_device_identity():
    identity = {"model": None, "serial": None, "uuid": None}
    try:
        inv = cli.cli("show inventory")
        identity.update(parse_show_inventory(inv))
    except Exception:
        pass

    try:
        hyp = cli.cli("show platform software system hypervisor")
        for line in hyp.splitlines():
            if "UUID:" in line:
                identity["uuid"] = line.split("UUID:")[1].strip()
    except Exception:
        pass
    return identity

# --------------------------
# Apply configuration
# --------------------------
def apply_config_text(config_text):
    commands = [ln.strip() for ln in config_text.splitlines() if ln.strip()]
    print("Applying config:")
    for c in commands:
        print("  ", c)
    cli.configurep(commands)
    cli.cli("write memory")

# --------------------------
# Main
# --------------------------
def main():
    identity = get_device_identity()
    if not identity.get("uuid"):
        print("UUID not found via CLI, abort.")
        return

    payload = {"uuid": identity["uuid"], "model": identity["model"]}
    data = post_json(GET_CONFIG_URL, payload)
    if not data:
        print("No response from server, abort.")
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
