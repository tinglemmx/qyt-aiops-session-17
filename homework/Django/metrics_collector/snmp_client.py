from pysnmp.hlapi import SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity, getCmd

def snmp_get(ip, community, oid, port=161):
    iterator = getCmd(
        SnmpEngine(),
        CommunityData(community, mpModel=1),
        UdpTransportTarget((ip, port)),
        ContextData(),
        ObjectType(ObjectIdentity(oid))
    )

    try:
        result = next(iterator)
    except TypeError:
        result = iterator  #
    except Exception as e:
        return False, {'value': None, 'error_msg': f"SNMP GET Exception: {e}"}
    
    errorIndication, errorStatus, errorIndex, varBinds = result

    if errorIndication:
        return False, {'value': None, 'error_msg': str(errorIndication)}
    elif errorStatus:
        msg = "{} at {}".format(
            errorStatus.prettyPrint(),
            errorIndex and varBinds[int(errorIndex) - 1][0] or "?"
        )
        return False, {'value': None, 'error_msg': msg}
    else:
        result_value = varBinds[0][1].prettyPrint() if varBinds else None
        if result_value is None:
             return False, {'value': None, 'error_msg': 'result is None'}
        if "no such" in result_value.lower():
            return False, {'value': None, 'error_msg': result_value }
        return True, {'value': result_value, 'error_msg': None}

    
if __name__ == "__main__":
    print(snmp_get('172.17.9.221', 'public', '.1.3.6.1.2.1.1.5.0'))