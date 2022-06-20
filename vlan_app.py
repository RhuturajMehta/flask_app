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

def get_vlan(device):

    with InitNornir() as nr:
        nr.inventory.hosts[device].username = config('USERNAME')
        nr.inventory.hosts[device].password = config('KEY')
    nr = nr.filter(name=device)
    
    results = nr.run(netmiko_send_command, command_string="show vlan")

    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_vlan.textfsm", "r") as t:

        template = TextFSM(t)
    
    result_for_parsing = results[device][0].result
    parsed_result = template.ParseText(result_for_parsing)
    collection_of_results = [dict(zip(template.header, pr)) for pr in parsed_result]

    purgedata = [i for i in collection_of_results if not i['STATUS'].startswith("act/unsup")]
    purgedata1 = [j for j in purgedata if not j['INTERFACES'] == []]
    #print(purgedata1)
    purgedata2 = [k for k in purgedata if not k['INTERFACES'] != []]
    #print(purgedata2)

    enterprise_vlan_list = open("enterprise_vlans.txt", "r")
    data_read = enterprise_vlan_list.read()
    #print(data_read)
    enterprise_vlan = data_read.split("\n")
    #print(enterprise_vlan,type(enterprise_vlan))
    
    sortedvlan1 = list(filter(lambda x:x["VLAN_ID"] in enterprise_vlan,purgedata2))
    sortedvlan2 = list(filter(lambda x:x["VLAN_ID"] not in enterprise_vlan,purgedata2))
    #print(sortedvlan2)

    return purgedata1,sortedvlan1,sortedvlan2