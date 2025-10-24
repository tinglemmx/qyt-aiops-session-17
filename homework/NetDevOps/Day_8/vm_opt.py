#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量恢复 vSphere 资源池中虚机的快照，并重新开机。
支持并发、自动关机、安全恢复。

依赖: pip install pyvmomi
"""

import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim


# --------------------
# vCenter 登录信息
# --------------------
VCENTER = "192.168.76.101"
USER = "administrator@test.local"
PWD = "VMware1!"
PORT = 443
RESOURCE_POOL_NAME = "my_rp_1"
SNAPSHOT_NAME = "init"
MAX_WORKERS = 5


# --------------------
# 工具函数
# --------------------
def wait_for_task(task):
    """等待 vSphere 异步任务完成"""
    while True:
        state = task.info.state
        if state == vim.TaskInfo.State.success:
            return True
        elif state == vim.TaskInfo.State.error:
            raise Exception(task.info.error.msg)
        time.sleep(1)


def get_resource_pool_by_name(content, pool_name):
    """根据名称查找资源池"""
    container = content.rootFolder
    view = content.viewManager.CreateContainerView(container, [vim.ResourcePool], True)
    for rp in view.view:
        if rp.name == pool_name:
            return rp
    return None


def get_snapshot_by_name(vm, snap_name):
    """递归查找虚机快照"""
    if not vm.snapshot:
        return None

    def traverse(snapshots):
        for snap in snapshots:
            if snap.name == snap_name:
                return snap.snapshot
            child = traverse(snap.childSnapshotList)
            if child:
                return child
        return None

    return traverse(vm.snapshot.rootSnapshotList)


def revert_vm(vm, snapshot_name):
    """单台虚机恢复快照并重启"""
    print(f"\n[VM] {vm.name}")

    snapshot = get_snapshot_by_name(vm, snapshot_name)
    if not snapshot:
        print(f"Snapshot '{snapshot_name}' not found, skip.")
        return

    # 如果开机则关机
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        print("Powering off...")
        wait_for_task(vm.PowerOffVM_Task())

    # 恢复快照
    print(f"Reverting to snapshot '{snapshot_name}'...")
    wait_for_task(snapshot.RevertToSnapshot_Task())

    # 开机
    print("Powering on...")
    wait_for_task(vm.PowerOnVM_Task())

    print("Done.")


# --------------------
# 主执行逻辑
# --------------------
def main():
    # 关闭 SSL 验证（实验环境用）
    context = ssl._create_unverified_context()
    si = SmartConnect(host=VCENTER, user=USER, pwd=PWD, port=PORT, sslContext=context)
    content = si.RetrieveContent()

    print(f"Connected to vCenter: {VCENTER}")

    rp = get_resource_pool_by_name(content, RESOURCE_POOL_NAME)
    if not rp:
        print(f"Resource pool '{RESOURCE_POOL_NAME}' not found.")
        Disconnect(si)
        return

    vms = rp.vm
    print(f"Found {len(vms)} VMs in pool '{RESOURCE_POOL_NAME}'")

    # 并发执行任务
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_vm = {executor.submit(revert_vm, vm, SNAPSHOT_NAME): vm for vm in vms}
        for future in as_completed(future_to_vm):
            vm = future_to_vm[future]
            try:
                future.result()
            except Exception as e:
                print(f"All tasks completed.")
    Disconnect(si)


if __name__ == "__main__":
    main()
