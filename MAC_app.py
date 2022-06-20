import os

from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command
from textfsm import TextFSM
from decouple import config

def get_MAC(device):

    with InitNornir() as nr:
        nr.inventory.hosts[device].username = config('USERNAME')
        nr.inventory.hosts[device].password = config('KEY')
    nr = nr.filter(name=device)
    
    results1 = nr.run(netmiko_send_command, command_string="show interface status")
    #print_result(results1)

    with open( os.getcwd() + "/ntc_templates/templates/cisco_ios_show_interfaces_status.textfsm", "r") as t1:

        template1 = TextFSM(t1)
                
    result_for_parsing1 = results1[device][0].result
    parsed_result1 = template1.ParseText(result_for_parsing1)
    collection_of_results1 = [dict(zip(template1.header, pr1)) for pr1 in parsed_result1]

    connected_switchports = list(filter(lambda x:x["STATUS"]=="connected",collection_of_results1))

    filter_PO = list(filter(lambda x:x["TYPE"]=="",connected_switchports))
    
    PO_ports = []

    for ports in filter_PO:
        PO_ports.append(ports["PORT"])

    if PO_ports == ['Po48']:
        results2 = nr.run(netmiko_send_command, command_string="show mac address-table | in Vlan|Gi")
    elif PO_ports == ['Po1']:
        results2 = nr.run(netmiko_send_command, command_string="show mac address-table | in Vlan|Gi")
    else:
        if 'Po48' in PO_ports:
            PO_ports.remove("Po48")
        if 'Po1' in PO_ports:
            PO_ports.remove("Po1")
        PO_string = '|'.join([str(PO) for PO in PO_ports])
        results2 = nr.run(netmiko_send_command, command_string="show mac address-table | in Vlan|Gi|" + PO_string)

    with open( os.getcwd() + "/ntc_templates/templates/cisco_ios_show_mac-address-table.textfsm", "r") as t2:

        template2 = TextFSM(t2)
                
    result_for_parsing2 = results2[device][0].result
    parsed_result2 = template2.ParseText(result_for_parsing2)
    collection_of_results2 = [dict(zip(template2.header, pr2)) for pr2 in parsed_result2]
    sorted_collection_of_results2 = sorted(collection_of_results2, key = lambda i: i['PORT'])

    return connected_switchports,sorted_collection_of_results2