import asyncio

from pysnmp.hlapi.v3arch.asyncio import *
from pysnmp.smi.view import MibViewController
from pysnmp.smi import builder, view


class QytangSNMP:
    def __init__(self, ip, community, snmp_port=161, version='v2c'):
        self.ip = ip
        self.community = community
        self.snmp_port = snmp_port
        self.version = mapping_version(version)

    async def getCMD(self, oid_dict):
        snmpEngine = SnmpEngine()

        iterator = get_cmd(
            snmpEngine,
            CommunityData(self.community, mpModel=self.version),
            await UdpTransportTarget.create((self.ip, self.snmp_port)),
            ContextData(),
            # ObjectType(ObjectIdentity("SNMPv2-MIB", "sysDescr", 0)), # SNMPv2-MIB::sysDescr.0 → 1.3.6.1.2.1.1.1.0
            ObjectType(ObjectIdentity(oid_dict))
        )

        errorIndication, errorStatus, errorIndex, varBinds = await iterator
        return result_format(errorIndication, errorStatus, errorIndex, varBinds)

    async def getNext(self, oid_dict_list, lookupMib=False):
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await next_cmd(
            snmpEngine,
            CommunityData(self.community, mpModel=self.version),
            await UdpTransportTarget.create((self.ip, self.snmp_port)),
            ContextData(),
            ObjectType(ObjectIdentity(*oid_dict_list)),
            lookupMib=lookupMib
        )
        return result_format(errorIndication, errorStatus, errorIndex, varBinds)

    async def bulkCmd(self, oid_dict_list, maxRepetitions=10, lookupMib=False):
        snmpEngine = SnmpEngine()
        errorIndication, errorStatus, errorIndex, varBinds = await bulk_cmd(
            snmpEngine,
            CommunityData(self.community, mpModel=self.version),
            await UdpTransportTarget.create((self.ip, self.snmp_port)),
            ContextData(),
            0,
            maxRepetitions,
            ObjectType(ObjectIdentity(*oid_dict_list)),
            lookupMib=lookupMib
        )
        return result_format(errorIndication, errorStatus, errorIndex, varBinds)

    def getOID(self, oid_dict_list):
        snmpEngine = SnmpEngine()
        mibBuilder = builder.MibBuilder()
        mibViewController = view.MibViewController(mibBuilder)
        oid_object = ObjectIdentity(*oid_dict_list)
        oid_object.resolve_with_mib(mibViewController)
        base_oid = oid_object.get_oid()
        return base_oid.prettyPrint()

    def getSubtree(self, oid_dict_list, force_return_oid=False):
        base_oid = self.getOID(oid_dict_list)
        tmp_oid_dict_list = oid_dict_list
        result = []
        for _ in range(10):
            tmp_result = asyncio.run(self.getNext(
                tmp_oid_dict_list, force_return_oid))
            if tmp_result:
                result += tmp_result
                tmp_oid = tmp_result[0][0]
                tmp_oid_dict_list = [tmp_oid]
                if base_oid not in tmp_oid:
                    break
            else:
                print("由于没有收到数据终止获取信息")
                break
        return result


def result_format(errorIndication, errorStatus, errorIndex, varBinds):
    result = []
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
            result.append([x.prettyPrint() for x in varBind])
    return result


def mapping_version(version):
    match version:
        case 'v1':
            return 0
        case 'v2c':
            return 1
        case 'v3':
            return 3
        case _:
            raise ValueError('版本错误')
