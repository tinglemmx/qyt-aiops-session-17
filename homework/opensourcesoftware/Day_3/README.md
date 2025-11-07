设备配置


## C8KV配置
### grpc 配置
```bash
! 接口/状态信息
telemetry ietf subscription 666
 encoding encode-kvgpb
 filter xpath /process-cpu-ios-xe-oper:cpu-usage/cpu-utilization/five-seconds
 stream yang-push
 update-policy periodic 1000
 receiver ip address 172.17.9.210 57500 protocol grpc-tcp
telemetry ietf subscription 667
 encoding encode-kvgpb
 filter xpath /memory-ios-xe-oper:memory-statistics/memory-statistic
 stream yang-push
 update-policy periodic 1000
 receiver ip address 172.17.9.210 57500 protocol grpc-tcp
telemetry ietf subscription 671
 encoding encode-kvgpb
 filter xpath /interfaces-ios-xe-oper:interfaces/interface/statistics
 stream yang-push
 update-policy periodic 1000
 receiver ip address 172.17.9.210 57500 protocol grpc-tcp
```

### snmp配置
```bash
snmp-server community mylab RO
snmp-server host 172.17.9.210 version 2c mylab
snmp-server enable traps
```


