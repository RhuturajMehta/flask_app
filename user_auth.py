from tacacs_plus.client import TACACSClient
from tacacs_plus.flags import TAC_PLUS_ACCT_FLAG_START, TAC_PLUS_ACCT_FLAG_WATCHDOG, TAC_PLUS_ACCT_FLAG_STOP
import socket
from decouple import config

tacacs_server = 'IPaddress'
auth_key = config('AUTH')

def login(username, password):
    cli = TACACSClient(tacacs_server, 49, auth_key, timeout=10, family=socket.AF_INET)
    authen = cli.authenticate(username, password)
    if authen.valid:
        author = cli.authorize(username, arguments=[b"service=app", b"protocol="])
        if author.valid:
            role = author.arguments[0].decode('utf-8')
            if 'admin' in role.lower():
                priv = 'admin'
            elif 'core' in role.lower():
                priv = 'core'
            else:
                #print("User has authenticated successfully, but failed authorization.")
                #priv = 'team'
                priv = None
    else:
        #print("User failed authentication.")
        priv = None

    return priv