from netmiko import ConnectHandler
import pprint
import ipaddress
import jinja2
import asyncio
import threading
import os
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from day7_1_create_db import Router, engine

tasks = []
task_id = 1

pp = pprint.PrettyPrinter(indent=4)

# 连接数据库的会话
Session = sessionmaker(bind=engine)

base_dir = Path(__file__).resolve().parent
template_dir = base_dir / "templates"
template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
template_env = jinja2.Environment(loader=template_loader)


def render_template(template_file, template_data) -> list:
    template_file = template_env.get_template(template_file)
    result = template_file.render({'data': template_data})
    # print("[render_template] reslut:")
    # print(result)
    return [cmd for cmd in result.split('\n') if cmd.strip()]


def get_router_config(session):
    # 查询所有路由器
    all_routers = session.query(Router).all()

    for router in all_routers:
        # 每一个路由器最终配置命令的列表
        router_final_config_list = []

        # 提取路由器IP
        router_ip = router.ip
        # 提起路由器登录用户名
        login_username = router.username
        # 提起路由器登录密码
        login_password = router.password
        # 接口配置列表
        interface_config_list = []
        # 找到这个路由器的每一个接口
        for interface in router.interface:
            # 提取接口名字
            interface_name = interface.interface_name
            # 提起接口IP
            interface_ip = interface.ip
            # 提取接口掩码
            interface_mask = interface.mask
            # 将 ip mask 的格式 转成 ip/prefixlen
            ip_addr = ipaddress.IPv4Address(interface_ip)
            net = ipaddress.IPv4Network(
                f"{interface_ip}/{interface_mask}", strict=False)
            interface_address = f"{interface_ip}/{net.prefixlen}"
            # 把每一个接口配置的字典, 放入列表"interface_config_list"
            interface_config_list.append({"interface_name": interface_name,
                                          "interface_address": interface_address,
                                          })

        # pprint.pprint(interface_config_list)
        '''
        [{'interface_address': '172.17.9.216/24', 'interface_name': 'eth0'},
        {'interface_address': '1.1.1.1/32', 'interface_name': 'lo'}]
        '''
        router_final_config_list.extend(render_template(
            "vyos_interface.j2", interface_config_list))
        # 提取路由器OSPF进程的数据库条目
        router_ospf_process = router.ospf_process
        # 提取OSPF进程ID
        router_ospf_process_id = router_ospf_process.processid
        # 提取路由器router_id
        router_id = router_ospf_process.routerid

        # 产生OSPF配置的字典, 先写入OSPF进程ID和router_id
        ospf_dict = {"ospf_process_id": router_ospf_process_id,
                     "router_id": router_id}

        # OSPF网络配置列表
        ospf_network_list = []

        # 提取OSPF进程下的每一个Area
        for area in router_ospf_process.area:
            # 提取OSPF的区域ID
            ospf_area_id = area.area_id
            # 找到此OSPF区域下的每一个需要被宣告的网络
            for ospf_network in area.ospf_network:
                # 提取OSPF网络
                ospf_network_net = ospf_network.network
                # 提起OSPF反掩码
                ospf_network_wildmask = ospf_network.wildmask
                if ospf_network_wildmask == "0.0.0.0":
                    prefixlen = 32
                else:
                    prefixlen = ipaddress.IPv4Network(
                        f"{ospf_network_net}/{ospf_network_wildmask}", strict=False).prefixlen
                # 把区域ID, OSPF网络, OSPF反掩码放入OSPF网络配置列表"ospf_network_list"
                ospf_network_list.append({"area": ospf_area_id,
                                          "network": f"{ospf_network_net}/{prefixlen}"
                                          })
        # 把网络配置写入OSPF配置的字典"ospf_dic"
        ospf_dict["ospf_network_list"] = ospf_network_list
        # pprint.pprint(ospf_dict)
        """
        {'ospf_network_list': [{'area': 0, 'network': '10.1.1.0/24'},
                            {'area': 0, 'network': '1.1.1.1/32'}],
        'ospf_process_id': 1,
        'router_id': '1.1.1.1'}
        """
        router_final_config_list.extend(
            render_template("vyos_ospf.j2", ospf_dict))
        print("[get_router_config] config_result:")
        for cmd in router_final_config_list:
            print(cmd)
        add_task(router_ip, login_username,
                 login_password, router_final_config_list)


def netmiko_config_cred(ip, username, password, cmds_list, device_type='vyos'):
    device = {
        "device_type": device_type,
        "ip": ip,
        "username": username,
        "password": password,
    }
    with ConnectHandler(**device) as conn:
        output = conn.send_config_set(cmds_list)
        output += conn.commit()
        # 这里有个强校验Done的 但vyos 新版本不会回显Done 所以命令要改一下.
        output += conn.save_config(cmd="save && echo 'Done'")
    return output


async def async_netmiko(task_id, ip, username, password, cmds_list, device_type='vyos'):
    loop = asyncio.get_running_loop()
    print(f'ID: {task_id} Started')
    print(os.getpid(), threading.current_thread().ident)

    result = await loop.run_in_executor(
        None,  # 默认线程池
        netmiko_config_cred,
        ip, username, password, cmds_list, device_type
    )

    print(f'ID: {task_id} Stopped')
    return result


async def run_netmiko_tasks():
    results = await asyncio.gather(*tasks)
    for r in results:
        print(r)


def add_task(ip, username, password, cmds_list):
    global task_id
    tasks.append(async_netmiko(task_id, ip, username, password, cmds_list))
    task_id += 1


if __name__ == '__main__':
    with Session() as session:
        get_router_config(session)
    asyncio.run(run_netmiko_tasks())
