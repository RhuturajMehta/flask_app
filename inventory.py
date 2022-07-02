import yaml
import os
from os.path import join, dirname, realpath, exists

device = {}
SwAdevice = {}
SwBdevice = {}
SwCdevice = {}

def load_hosts_inventory(filename):
    return yaml.load(open(filename, "r"), Loader=yaml.SafeLoader)

file_exists = exists(os.getcwd() + '/hosts.yaml')
if file_exists == True:
    hosts = load_hosts_inventory("hosts.yaml")
    hostsSwA = load_hosts_inventory("Buildings/hostsSwA.yaml")
    hostsSwB = load_hosts_inventory("Buildings/hostsSwB.yaml")
    hostsSwC = load_hosts_inventory("Buildings/hostsSwC.yaml")

    inventory = []
    for host in hosts:
        inventory.append({"name": host, "mgmt_ip": hosts[host]["hostname"]})

    inventorySwA = []
    ups_ip_SwA = []
    cisco_ipA = []
    for hostSwA in hostsSwA:
        cisco_ipA.append(hostsSwA[hostSwA]["hostname"])
        ups_ip_SwA.append(hostsSwA[hostSwA]["ups"])
        inventorySwA.append({"name": hostSwA, "mgmt_ip": hostsSwA[hostSwA]["hostname"], "platform": hostsSwA[hostSwA]["platform"], "ups": hostsSwA[hostSwA]["ups"]})

    inventorySwB = []
    ups_ip_SwB = []
    cisco_ipB = []
    for hostSwB in hostsSwB:
        cisco_ipB.append(hostsSwB[hostSwB]["hostname"])
        ups_ip_SwB.append(hostsSwB[hostSwB]["ups"])
        inventorySwB.append({"name": hostSwB, "mgmt_ip": hostsSwB[hostSwB]["hostname"], "platform": hostsSwB[hostSwB]["platform"], "ups": hostsSwB[hostSwB]["ups"]})

    inventorySwC = []
    cisco_ipC = []
    for hostSwC in hostsSwC:
        cisco_ipC.append(hostsSwC[hostSwC]["hostname"])
        inventorySwC.append({"name": hostSwC, "mgmt_ip": hostsSwC[hostSwC]["hostname"], "platform": hostsSwC[hostSwC]["platform"]})