## Installation

Clone the repository into your Workstation:
```
git clone git@github.com:RhuturajMehta/flask_app.git

```

## Modifications

Add network devices (Cisco Cat 3850,9300,9400 only supported) to hosts.csv. 

For Buliding A use SwA, Building C use SwB, Core use SwC as building codes in hosts.csv file.

Update defaults.yaml for device creds and user_auth.py for tacacs server ip address

Create '.env' file for app variables - 

```
nano .env

USERNAME = username
KEY = password
AUTH = tacacs key
SNMP = switch/ups read-only snmp
```


### Linux/Mac Users

```
cd flask_app

./build.sh

./start_app_prod.sh
```
Use 'admin/admin' for login unless tacacs server is specified.