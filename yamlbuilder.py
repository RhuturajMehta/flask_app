import os
import shutil

ctr = 0
excel_filename = 'hosts.csv'
device = {}
SwAdevice = {}
SwBdevice = {}
SwCdevice = {}

with open(excel_filename, "r") as excel_csv:
    for line in excel_csv:
        if ctr == 0:
            ctr+=1
        else:
            hostname,ip,port,platform,group,ups,building = line.replace(' ','').strip().split(',')
            device[hostname] = {'hostname': ip, 'port': port, 'platform': platform, 'groups': group}
            if building == 'SwA':
                SwAdevice[hostname] = {'hostname': ip, 'platform': platform, 'ups': ups, 'groups': group}
            elif building == 'SwB':
                SwBdevice[hostname] = {'hostname': ip, 'platform': platform, 'ups': ups, 'groups': group}
            else:
                SwCdevice[hostname] = {'hostname': ip, 'platform': platform, 'groups': group}

def hostsyaml(device):
    yaml_filename = excel_filename.replace('csv', 'yaml')
    with open(yaml_filename, "w+") as yf :
        yf.write("--- \n")
        for d in device:
            yf.write(f"{d} : \n")
            for x,y in device[d].items():
                if x == 'port':
                    yf.write(f"  {x} : {y}\n")
                elif x == 'groups':
                    yf.write(f"  {x} : \n    - '{y}'\n")
                else:
                    yf.write(f"  {x} : '{y}'\n")
    return

def writeyaml(building,name):
    yaml_filename = excel_filename.replace('hosts.csv', 'hosts' + name + '.yaml')
    with open(yaml_filename, "w+") as yf :
        yf.write("--- \n")
        for b in building:
            yf.write(f"{b} : \n")
            for x,y in building[b].items():
                if x == 'groups':
                    yf.write(f"  {x} : \n    - '{y}'\n")
                else:
                    yf.write(f"  {x} : '{y}'\n")
    shutil.move(os.getcwd() + '/hosts' + name + '.yaml', os.getcwd() + '/Buildings')
    return

hosts_yaml = hostsyaml(device)
SwA_yaml = writeyaml(SwAdevice,'SwA')
SwB_yaml = writeyaml(SwBdevice,'SwB')
SwC_yaml = writeyaml(SwCdevice,'SwC')


