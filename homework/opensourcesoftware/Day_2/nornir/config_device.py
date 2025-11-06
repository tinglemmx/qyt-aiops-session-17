from nornir import InitNornir
from nornir.core.inventory import Host
from pathlib import Path
import pprint
from jinja2 import Environment, FileSystemLoader
from nornir_netmiko.tasks import netmiko_send_config
from nornir.core.task import Task, Result
from nornir_utils.plugins.functions import print_result
from netmiko.exceptions import ReadTimeout, NetmikoBaseException


pp = pprint.PrettyPrinter(indent=4)

BASE_DIR = Path(__file__).resolve().parent

nr = InitNornir(
    runner={
        "plugin": "threaded",
        "options": {
            "num_workers": 100,
        },
    },
    inventory={
        "plugin": "SimpleInventory",
        "options": {
            "host_file": BASE_DIR /"inventory"/"hosts.yaml",
            "group_file": BASE_DIR /"inventory"/"groups.yaml",
            "defaults_file": BASE_DIR /"inventory"/"defaults.yaml"
        },
    },
)

env = Environment(loader=FileSystemLoader(BASE_DIR/"templates"),
                  trim_blocks=True,
                  lstrip_blocks=True)

def render_template(task: Task, template_name: str) -> str:
    template = env.get_template(template_name)
    rendered_config = template.render(
                        hostname = task.host.name,
                        name_servers = task.host.get('name_servers', None),
                        domain_name = task.host.get('domain_name', None),
                        accounts = task.host.get('accounts', None),
                        interfaces = task.host.get('interfaces', None),
                        ospf = task.host.get('ospf', None),
                        logging = task.host.get('logging', None)  
                                      )
    return Result(host=task.host, result=rendered_config)
def push_csr_config(task):
    
    task.run(
        task=render_template,
        template_name="csr1000v_config.j2"
    )
    rendered_config = task.results[0].result

    task.run(
        task=netmiko_send_config,
        config_commands=rendered_config.splitlines()
        )
    
    return Result(host=task.host, result="Configuration pushed successfully.")



# 选择平台为 ios 的设备
csr_devices = nr.filter(platform="ios")
result = csr_devices.run(task=push_csr_config)
print_result(result)