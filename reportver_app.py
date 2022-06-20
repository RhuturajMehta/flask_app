import os
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from textfsm import TextFSM
from decouple import config

nornir = InitNornir('config.yaml')

results = nornir.run(netmiko_send_command, command_string="sh version")
nornir.close_connections()

def get_ver(switch):

    with open( os.getcwd() +"/ntc_templates/templates/cisco_ios_show_version.textfsm", "r") as t:

        template = TextFSM(t)
    
    result_for_parsing = results[switch][0].result
    parsed_result = template.ParseText(result_for_parsing)
    collection_of_results = [dict(zip(template.header, pr)) for pr in parsed_result]

    return collection_of_results


