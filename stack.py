import subprocess
from easysnmp import Session
from decouple import config

def ping_ip(device_ip_address):
        try:
            output = subprocess.check_output("ping -c 1 {}".format( device_ip_address ), shell=True, universal_newlines=True)
            if 'unreachable' in output:
                return False
            else:
                return True
        except Exception:
                return False

def stackstatus(device_ip_data):
    snmpdata=[]
    switch_status=[]
    switchdata = []
    for each in device_ip_data:
        if "Web-GUI" in (each):
            status = str(f"stack : Smart") 
        elif "None" in (each):
            status = str(f"stack : None") 
        elif ping_ip(each):
            session = Session(hostname=each, community=config('SNMP'), version=2)
            snmpdata = session.walk('.1.3.6.1.4.1.9.9.500.1.2.1.1.1')
            if snmpdata == []:
                status = str(f"stack : Chassis")
            else:
                status = str(f"stack : {len(snmpdata)}")
        else:
            status = str(f"stack : Offline") 
        switch_status.append(status)
    e = {}
    for c in switch_status:
        j = c.split(' : ')
        e[j[0]] = j[1]
        switchdata.append(dict(e.items()))
    return switchdata