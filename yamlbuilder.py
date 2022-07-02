import os
from os.path import join, dirname, realpath, exists
import yaml
import shutil
import subprocess

def hostsyaml(device):
    
    file_exists = exists(os.getcwd() + 'hosts.yaml')
    if file_exists == True:
        os.remove(os.getcwd() + '/hosts.yaml' )    
    
    excel_filename = os.getcwd() + '/static/files/hosts.csv'
    yaml_filename = excel_filename.replace(excel_filename, 'hosts.yaml')
    
    with open(yaml_filename, "w") as yf :
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
    
    file_exists = exists(os.getcwd() + '/Buildings/hosts' + name + '.yaml')
    if file_exists == True:
        os.remove(os.getcwd() + '/Buildings/hosts' + name + '.yaml' ) 

    excel_filename = os.getcwd() + '/static/files/hosts.csv'
    yaml_filename = excel_filename.replace(excel_filename, 'hosts' + name + '.yaml')

    with open(yaml_filename, "w") as yf :
        yf.write("--- \n")
        for b in building:
            yf.write(f"{b} : \n")
            for x,y in building[b].items():
                if x == 'groups':
                    yf.write(f"  {x} : \n    - '{y}'\n")
                else:
                    yf.write(f"  {x} : '{y}'\n")                   
    
    shutil.move(os.getcwd() + '/hosts' + name + '.yaml', os.getcwd() + '/Buildings')
    subprocess.run(["pkill", "-f", "gunicorn"])  
    return