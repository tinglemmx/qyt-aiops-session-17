# 预备和检查

## 预配

```bash
terminal length 0
config term
username admin privilege 15 password 0 Cisc0123
interface GigabitEthernet4
 ip address 172.17.9.215 255.255.255.0
 no shutdown
aaa new-model
aaa authentication login default local
aaa authorization exec default local 
aaa authorization commands 15 default local 
line con 0
 exec-timeout 0 0



terminal length 0
config term
username admin privilege 15 password 0 Cisc0123
interface GigabitEthernet4
 ip address 172.17.9.216 255.255.255.0
 no shutdown
aaa new-model
aaa authentication login default local
aaa authorization exec default local 
aaa authorization commands 15 default local 
line con 0
 exec-timeout 0 0
```


## 检查

```bash
show running-config | s name-server
show running-config | s domain
show running-config | s username
show running-config | s interface
show running-config | s ospf
show running-config | s logging

```