from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, ContextData, UdpTransportTarget, ObjectType, ObjectIdentity

snmpEngine = SnmpEngine()
iterator = getCmd(
    snmpEngine,
    CommunityData('mylab', mpModel=1),
    UdpTransportTarget(('192.0.2.210', 161)),
    ContextData(),
    ObjectType(ObjectIdentity(".1.3.6.1.4.1.9.9.48.1.1.1.6.1"))
)

def result_format(errorIndication, errorStatus, errorIndex, varBinds):
    result = []
    if errorIndication:
        print(errorIndication)
        return False, {'value': None, 'error_msg': str(errorIndication)}

    elif errorStatus:
        msg = "{} at {}".format(
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or "?"
        )
        print(msg)
        return False, {'value': None, 'error_msg': msg}
    else:
        for varBind in varBinds:
            result.append([x.prettyPrint() for x in varBind])
    return True, {'value': result[0][1], 'error_msg': None}

# 正确取值
errorIndication, errorStatus, errorIndex, varBinds = iterator

print(result_format(errorIndication, errorStatus, errorIndex, varBinds))