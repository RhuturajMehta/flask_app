import os
from nornir import InitNornir
from nornir_utils.plugins.functions import print_result
from nornir_netmiko.tasks import netmiko_send_command, netmiko_send_config
from netmiko import ConnectHandler
from textfsm import TextFSM
from decouple import config

def merge(list1,list2):
    for m,n in zip(list1,list2):
        (m.update(n))
    return list1

def get_auth_open(device):

    with InitNornir() as nr:
        nr.inventory.hosts[device].username = config('USERNAME')
        nr.inventory.hosts[device].password = config('KEY')
        switch_ip = nr.inventory.hosts[device].hostname
    nr = nr.filter(name=device)
    
    results3 = nr.run(netmiko_send_command, command_string="show run | in authentication open|switchport|interface")
    
    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_run_interfaces.textfsm", "r") as t3:

        template3 = TextFSM(t3)
    
    result_for_parsing3 = results3[device][0].result
    parsed_result3 = template3.ParseText(result_for_parsing3)
    collection_of_results3 = [dict(zip(template3.header, pr3)) for pr3 in parsed_result3]
    if collection_of_results3[4]["INTERFACE"] == "GigabitEthernet0/0":
        del collection_of_results3[0:5]
    elif collection_of_results3[2]["INTERFACE"] == "GigabitEthernet0/0":
        del collection_of_results3[0:3]
    elif collection_of_results3[1]["INTERFACE"] == "GigabitEthernet0/0":
        del collection_of_results3[0:2]
    else:
        del collection_of_results3[0:1]

    results4 = nr.run(netmiko_send_command, command_string="show interface")

    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_interfaces.textfsm", "r") as t4:

        template4 = TextFSM(t4)
        
    result_for_parsing4 = results4[device][0].result
    parsed_result4 = template4.ParseText(result_for_parsing4)
    collection_of_results4 = [dict(zip(template4.header, pr4)) for pr4 in parsed_result4]
    del collection_of_results4[0:3]

    sortedauthresults = list(filter(lambda x:x["AUTHENTICATION"]=="open",merge(collection_of_results3,collection_of_results4)))

    results5 = nr.run(netmiko_send_command, command_string="show device-tracking database | in ARP")
    
    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_device-tracking_database.textfsm", "r") as t5:

        template5 = TextFSM(t5)
                    
    result_for_parsing5 = results5[device][0].result
    parsed_result5 = template5.ParseText(result_for_parsing5)
    collection_of_results5 = [dict(zip(template5.header, pr5)) for pr5 in parsed_result5]
    del collection_of_results5[0:1]

    purgedata = [i for i in collection_of_results5 if not i['ADDRESS'].startswith("169.")]
    devicedata = sorted(purgedata, key = lambda i: i['INTERFACE'])
    #print(devicedata)

    #nr.close_connections()

    switch_device = {
        "device_type": "cisco_ios",
        "host": switch_ip,
        "username": config('USERNAME'),
        "password": config('KEY'),
        "fast_cli": False,
    }

    with ConnectHandler(**switch_device) as net_connect:
        results6 = net_connect.send_command("show auth session", delay_factor=0.25)

    #results6 = nr.run(netmiko_send_command, command_string="show authentication sessions")
    #print_result(results6)

    with open("/Users/rh47691/flask_app/ntc_templates/templates/cisco_ios_show_authentication_sessions.textfsm", "r") as t6:

        template6 = TextFSM(t6)
            
    #result_for_parsing6 = results6[device][0].result
    #print(result_for_parsing6,type(result_for_parsing6))
    parsed_result6 = template6.ParseText(results6)
    collection_of_results6 = [dict(zip(template6.header, pr6)) for pr6 in parsed_result6]
    print(collection_of_results6)

    authdata = sorted(collection_of_results6, key = lambda i: i['INTERFACE'])

    interfaceGi = []
    interfaceTw = []
    interfaceTe = []

    for intf in sortedauthresults:
        if intf["INTERFACE"].startswith("Gi"):
            editGi = intf["INTERFACE"].replace("gabitEthernet","")
            #print(editGi,type(editGi))
            sorteddeviceGi = list(filter(lambda x:x["INTERFACE"]==editGi,devicedata))
            sortedauthGi = list(filter(lambda x:x["INTERFACE"]==editGi,authdata))
            interfaceGi.extend(merge(sorteddeviceGi,sortedauthGi))
        elif intf["INTERFACE"].startswith("Tw"):
            editTw = intf["INTERFACE"].replace("oGigabitEthernet","")
            sorteddeviceTw = list(filter(lambda x:x["INTERFACE"]==editTw,devicedata))
            sortedauthTw = list(filter(lambda x:x["INTERFACE"]==editTw,authdata))
            interfaceTw.extend(merge(sorteddeviceTw,sortedauthTw))
        elif intf["INTERFACE"].startswith("Te"):
            editTe = intf["INTERFACE"].replace("nGigabitEthernet","")
            sorteddeviceTe = list(filter(lambda x:x["INTERFACE"]==editTe,devicedata))
            sortedauthTe = list(filter(lambda x:x["INTERFACE"]==editTe,authdata))
            interfaceTe.extend(merge(sorteddeviceTe,sortedauthTe))        

    interfacedata = interfaceGi + interfaceTw + interfaceTe



    return sortedauthresults,interfacedata



