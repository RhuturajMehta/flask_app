import subprocess
from easysnmp import Session
from decouple import config

def ping_ip(device_ip_address):
        try:
            output = subprocess.check_output("ping -c 1 -W 1 {}".format( device_ip_address ), shell=True, universal_newlines=True)
            if 'unreachable' in output:
                return False
            else:
                return True
        except Exception:
                return False

def stackstatus(device_ip_data):
    snmpdata=[]
    cisco_status=[]
    ciscodata = []
    for each in device_ip_data:
        if "Web-GUI" in (each):
            status = str(f"stack : Smart Switch") 
        elif ping_ip(each):
            session = Session(hostname=each, community=config('SNMP'), version=2)
            snmpdata = session.walk('.1.3.6.1.4.1.9.9.500.1.2.1.1.1')
            if snmpdata == []:
                status = str(f"stack : Chassis Switch")
            else:
                status = str(f"stack : {len(snmpdata)} Switch")
        else:
            status = str(f"stack : Offline") 
        cisco_status.append(status)
    e = {}
    for c in cisco_status:
        j = c.split(' : ')
        e[j[0]] = j[1]
        ciscodata.append(dict(e.items()))
    return ciscodata