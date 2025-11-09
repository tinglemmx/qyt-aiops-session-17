

# 设备配置

```BASH
flow record Qytang-Record
 match ipv4 source address
 match ipv4 destination address
 match ipv4 protocol
 match transport destination-port
 match transport source-port
 match interface input
 match ipv4 tos
 match transport tcp flags
 match ipv4 version
 match routing source as
 match routing destination as
 match datalink destination-vlan-id
 match datalink source-vlan-id
 match ipv4 section header size 100
 match ipv4 id
 collect counter bytes
 collect timestamp sys-uptime first
 collect timestamp sys-uptime last
!
!
flow exporter Netflow-Exporter
 destination 172.17.9.210
 transport udp 2055
 template data timeout 30
!
!
flow monitor Monitor1
 exporter Netflow-Exporter
 record Qytang-Record
!
!
interface GigabitEthernet1
 ip flow monitor Monitor1 input
 ip flow monitor Monitor1 output
 ip address 172.17.9.215 255.255.255.0
 negotiation auto
!
interface GigabitEthernet2
 ip flow monitor Monitor1 input
 ip flow monitor Monitor1 output
 no ip address
 negotiation auto
!
interface GigabitEthernet2.100
 encapsulation dot1Q 100
 ip flow monitor Monitor1 input
 ip flow monitor Monitor1 output
 ip address 192.168.1.1 255.255.255.0
!
```