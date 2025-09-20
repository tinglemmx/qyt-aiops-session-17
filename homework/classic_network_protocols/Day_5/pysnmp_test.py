import asyncio
from pysnmp.hlapi.v3arch.asyncio import *

'''


        with SNMPv1, community ‘public’

        over IPv4/UDP

        to an Agent at demo.snmplabs.com:161

        for an instance of SNMPv2-MIB::sysDescr.0 MIB object

        Based on asyncio I/O framework



'''
async def run():
    snmpEngine = SnmpEngine()

    iterator = get_cmd(
        snmpEngine,
        CommunityData("cisco@123", mpModel=0),
        await UdpTransportTarget.create(("172.17.9.216", 161)),
        ContextData(),
        # ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)), # SNMPv2-MIB::sysDescr.0 → 1.3.6.1.2.1.1.1.0
        ObjectType(ObjectIdentity(".1.3.6.1.4.1.2021.10.1.3.1"))
    )

    errorIndication, errorStatus, errorIndex, varBinds = await iterator

    if errorIndication:
        print(errorIndication)

    elif errorStatus:
        print(
            "{} at {}".format(
                errorStatus.prettyPrint(),
                errorIndex and varBinds[int(errorIndex) - 1][0] or "?",
            )
        )
    else:
        for varBind in varBinds:
            
            print(" = ".join([x.prettyPrint() for x in varBind]))
            print(varBind[1].prettyPrint())

    snmpEngine.close_dispatcher()


asyncio.run(run())


'''
Sending SNMP TRAP’s and INFORM’s is as easy with PySNMP library. The following code sends SNMP TRAP:

    SNMPv1

    with community name ‘public’

    over IPv4/UDP

    send TRAP notification

    with Generic Trap #1 (warmStart) and Specific Trap 0

    with default Uptime

    with default Agent Address

    with Enterprise OID 1.3.6.1.4.1.20408.4.1.1.2

    include managed object information ‘1.3.6.1.2.1.1.1.0’ = ‘my system’
    

'''
# async def run():
#     snmpEngine = SnmpEngine()
#     errorIndication, errorStatus, errorIndex, varBinds = await send_notification(
#         snmpEngine,
#         CommunityData("cisco@123", mpModel=0),
#         await UdpTransportTarget.create(("172.17.9.216", 161)),
#         ContextData(),
#         "trap",
#         NotificationType(ObjectIdentity("1.3.6.1.6.3.1.1.5.2"))
#         .load_mibs("SNMPv2-MIB")
#         .add_varbinds(
#             ("1.3.6.1.6.3.1.1.4.3.0", "1.3.6.1.4.1.20408.4.1.1.2"),
#             ("1.3.6.1.2.1.1.1.0", OctetString("my system")),
#         ),
#     )

#     if errorIndication:
#         print(errorIndication)

#     snmpEngine.close_dispatcher()


# asyncio.run(run())