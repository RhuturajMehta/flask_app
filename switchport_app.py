import os

from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from textfsm import TextFSM
from decouple import config

def merge(list1,list2):
    for x,y in zip(list1,list2):
       (x.update(y)) 
    return list1 

def get_data(device):

    with InitNornir() as nr:
        nr.inventory.hosts[device].username = config('USERNAME')
        nr.inventory.hosts[device].password = config('KEY')
    nr = nr.filter(name=device)
    
    results = nr.run(netmiko_send_command, command_string="show version")

    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_version.textfsm", "r") as t:

        template = TextFSM(t)
    
    result_for_parsing = results[device][0].result
    parsed_result = template.ParseText(result_for_parsing)
    collection_of_results = [dict(zip(template.header, pr)) for pr in parsed_result]

    results1 = nr.run(netmiko_send_command, command_string="show interface")

    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_interfaces.textfsm", "r") as t1:

        template1 = TextFSM(t1)
    
    result_for_parsing1 = results1[device][0].result
    parsed_result1 = template1.ParseText(result_for_parsing1)
    collection_of_results1 = [dict(zip(template1.header, pr1)) for pr1 in parsed_result1]
    del collection_of_results1[0:3]

    results2 = nr.run(netmiko_send_command, command_string="show interface switchport")
    
    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_interfaces_switchport.textfsm", "r") as t2:

        template2 = TextFSM(t2)
    
    result_for_parsing2 = results2[device][0].result
    parsed_result2 = template2.ParseText(result_for_parsing2)
    collection_of_results2 = [dict(zip(template2.header, pr2)) for pr2 in parsed_result2]

    interface_data = merge(collection_of_results1,collection_of_results2)

    sortedlink1 = list(filter(lambda x:x["LINK_STATUS"]=="down",interface_data))
    sortedlink2 = list(filter(lambda x:x["LINK_STATUS"]=="administratively down",interface_data))
    sortedlink= sortedlink1 + sortedlink2
    sortedint = list(filter(lambda x:x["MEDIA_TYPE"]=="10/100/1000BaseTX",sortedlink))
    sortedint1 = list(filter(lambda x:x["MEDIA_TYPE"]=="100/1000/2.5GBaseTX",sortedlink))
    sortedint2 = list(filter(lambda x:x["MEDIA_TYPE"]=="100/1000/2.5G/5G/10GBaseTX",sortedlink))
    sortedint3 = list(filter(lambda x:x["MEDIA_TYPE"]=="10/100BaseTX",sortedlink))
    finaldata = sortedint + sortedint1 + sortedint2 + sortedint3

    data = collection_of_results + finaldata

    nr.close_connections()

    return data