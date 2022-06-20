import subprocess
from easysnmp import Session
from decouple import config

def ping_ip(ups_ip_address):
        try:
            output = subprocess.check_output("ping -c 1 -W 2 {}".format( ups_ip_address ), shell=True, universal_newlines=True)
            if 'unreachable' in output:
                return False
            else:
                return True
        except Exception:
                return False

def upsstatus(ups_ip_data):
    snmpdata=[]
    ups_status=[]
    upsdata = []
    for each in ups_ip_data:
        if "None" in (each):
            status = str(f"status : None")
        elif ping_ip(each):
            try:
                session = Session(hostname=each, community=config('SNMP'), version=2)
                snmpdata = session.get('.1.3.6.1.4.1.318.1.1.1.2.2.4.0')
                if snmpdata.value == '1':
                    snmpdata1 = session.get('.1.3.6.1.4.1.318.1.1.1.2.2.3.0')
                    ups_rt = (int(snmpdata1.value))//6000
                    status = str(f"status : Battery OK - Runtime {ups_rt} minutes")
                else:
                    status = str("status : Online / Replace Battery")
            except:
                print(f"{each} is online/Update SNMP")
        else:
            status = str("status : Offline") 
        ups_status.append(status)
    d = {}
    for b in ups_status:
        i = b.split(' : ')
        d[i[0]] = i[1]
        upsdata.append(dict(d.items()))
    return upsdata