#!/bin/bash
while true; do
    cores=$(nproc)
    # 随机选择核数
    n=$((RANDOM % cores + 1))
    echo "Load $n cores..."
    for _ in $(seq 1 $n); do
        sha1sum /dev/zero &   # 背景高负载任务
    done
    sleep 5
    pkill sha1sum
    sleep $((RANDOM % 5 + 1))
done