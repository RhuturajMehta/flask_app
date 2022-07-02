from flask import Flask, request, render_template, url_for, flash, redirect, session, Markup, send_from_directory
from forms import LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin

from yamlbuilder import *
from inventory import *
from ups import *
from stack import *
from switchport_app import *
from authopen_app import *
#from reportver_app import *
from vlan_app import *

import user_auth as auth

def merge(list1,list2):
    for x,y in zip(list1,list2):
       (x.update(y)) 
    return list1 

user_dict = {}
user_access = []

class User():
    def __init__(self, username, password):
        self.username = username
        self.password = password

        #if username == 'admin' and password == 'admin':
        if username == 'admin':
            priv = 'owner'
        else:
        # Send TACACS authentication and authorization requests
            priv = auth.login(self.username, self.password)

        if priv:
            self.is_authenticated = True
            self.is_active = True
            self.is_anonymous = False
            if priv == 'owner':
                self.priv_lvl = 3
            elif priv == 'core':
                self.priv_lvl = 2
            elif priv == 'team':
                self.priv_lvl = 1               
        else:
            self.is_authenticated = False
            self.is_anonymous = True
            self.priv_lvl = -1

    def get_id(self):
        return self.username


app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(2048)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['TEMPLATES_AUTO_RELOAD'] = True

UPLOAD_FOLDER = 'static/files'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER
   
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' 

@login_manager.user_loader
def load_user(user):
    global user_dict
    if user in user_dict.keys():
        return user_dict[user]

@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()

    try:
        if user.is_authenticated:
            return render_template('main.html')
    except UnboundLocalError:
        user = None
        pass

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User(username, password)
        username = password = None

        if user.priv_lvl == 1:
            login_user(user, remember=form.remember.data)
            user_dict.update({
                user.username : user
            })
            user_access.append(user.priv_lvl)
            return render_template('main_team.html', current_user=current_user, user=user)

        elif user.priv_lvl == 2:
            login_user(user, remember=form.remember.data)
            user_dict.update({
                user.username : user
            })
            user_access.append(user.priv_lvl)
            return render_template('main_core.html', current_user=current_user, user=user)

        elif user.priv_lvl == 3:
            login_user(user, remember=form.remember.data)
            user_dict.update({
                user.username : user
            })
            user_access.append(user.priv_lvl)

            return render_template('main.html', current_user=current_user, user=user)

        else:
            flash(f'Invalid login', 'error')
            return render_template('index.html', title='Login Required', form=form, user=user)

    return render_template('index.html', title='Login Required', form=form, user=user)

@app.route('/logout')
def logout():
    session.pop('_user_id')
    return redirect(url_for('index'))

@app.route('/main', methods=['GET'])
@login_required
def main():
    name = "Access Dashboard"
    return render_template("main.html", title="NetOps", name="NetOps")

@app.route('/main/inventory')
def inventory():
    return render_template('inventory.html')

@app.route("/upload", methods=['POST'])
def upload():
      # get the uploaded file
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        csv_filename = file_path.replace(file_path, 'static/files/hosts.csv')
          # set the file path
        uploaded_file.save(csv_filename)
          # save the file
    return redirect(url_for('inventory_success'))

@app.route('/inventory_success')
def inventory_success():

    file_exists = exists(os.getcwd() + '/static/files/hosts.csv')
    if file_exists == True:
        excel_filename = os.getcwd() + '/static/files/hosts.csv'

        ctr = 0
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

        hosts_yaml = hostsyaml(device)
        SwA_yaml = writeyaml(SwAdevice,'SwA')
        SwB_yaml = writeyaml(SwBdevice,'SwB')
        SwC_yaml = writeyaml(SwCdevice,'SwC')
    
    return render_template('inventory.html')

@app.route('/main_core', methods=['GET'])
@login_required
def main_core():
    name = "Core Dashboard"
    return render_template("main_core.html", title="NetOps", name="NetOps")   

@app.route('/main/location', methods=['GET'])
@login_required
def location():
    name = "Campus Access Switches"
    return render_template("location.html", title="NetOps", name="NetOps")

@app.route('/license', methods=['GET'])
@login_required
def license():
    name = "license" 
    with open(os.getcwd() + '/LICENSE', 'r') as f: 
        return render_template('license.html', title="license", name="license", text=f.read())

@app.route('/report_ver', methods=['GET'])
@login_required
def report():
    name = "report_ver"
    verlist = [] 
    for a in nornir.inventory.hosts:
        verlist.append(get_ver(a))
    return render_template("report_ver.html", fact=verlist)

@app.route('/pdf', methods=['GET'])
@login_required
def pdf():
    name = "pdf" 
    workingdir = os.path.abspath(os.getcwd())
    filepath = workingdir + '/static/files/'
    return send_from_directory(filepath, 'python_ise.pdf') 

@app.route('/main/SwA', methods=['GET'])
@login_required
def NtwkSwA():
    name = "SwA"
    swstackA = stackstatus(cisco_ipA)
    upsdataSwA = upsstatus(ups_ip_SwA)
    sw_upsA = merge(swstackA,upsdataSwA)
    inventorySw_dataA = merge(inventorySwA,sw_upsA)
    return render_template("Campus.html", title="SwA", name="SwA", inventory = inventorySw_dataA)

@app.route('/main/SwB', methods=['GET'])
@login_required
def NtwkSwB():
    name = "SwB"
    swstackB = stackstatus(cisco_ipB)
    upsdataSwB = upsstatus(ups_ip_SwB)
    sw_upsB = merge(swstackB,upsdataSwB)
    inventorySw_dataB = merge(inventorySwB,sw_upsB)
    return render_template("Campus.html", title="SwB", name="SwB", inventory = inventorySw_dataB)

@app.route('/main_core/core', methods=['GET'])
@login_required
def NtwkSwC():
    name = "SwC"
    swstackC = stackstatus(cisco_ipC)
    inventorySw_dataC = merge(inventorySwC,swstackC)
    return render_template("Core.html", title="SwC", name="SwC", inventory = inventorySw_dataC)

@app.route('/main/config/<string:device_name>', methods=['GET'])
#@login_required
def config(device_name):
    name = "config" 
    with open('/Users/rh47691/flask_app/config_backup/'+ hosts[device_name]["hostname"] + '.txt', 'r') as f: 
        return render_template('config.html', title="config", name="config", device_name=device_name, text=f.read())

@app.route('/main/facts/<string:device_name>', methods=['GET'])
@login_required
def display_facts(device_name):
    interface_finaldata = get_data(device_name)
    facts = interface_finaldata[0]
    del interface_finaldata[0:1]
    if interface_finaldata == []:
        return render_template("facts_zero.html", device_name=device_name)
    else: 
        sortedfinaldata = interface_finaldata
        return render_template("facts.html", device_name=device_name, fact=facts, interface=sortedfinaldata )

@app.route('/main/auth_facts/<string:device_name>', methods=['GET'])
@login_required
def display_auth_facts(device_name):
    hostname = {}
    hostname['HOSTNAME'] = (device_name)
    sortedauth = get_auth_open(device_name)
    sortedauthopen = sortedauth[0]
    sortedauthdata = sortedauth[1]
    sortedauthint = sortedauth[2]
    if sortedauth == ([],[],[]):
        return render_template("auth_facts_zero.html", device_name=device_name, fact=hostname)
    else:
        if sortedauthint == []: 
            return render_template("auth_facts.html", device_name=device_name, fact=hostname, interface_auth = sortedauthopen, auth_data = sortedauthdata )
        else :
           return render_template("auth_facts_int.html", device_name=device_name, fact=hostname, interface_auth = sortedauthopen, auth_data = sortedauthdata, int_data = sortedauthint ) 

@app.route('/main_core/vlan_facts/<string:device_name>', methods=['GET'])
@login_required
def display_vlan_facts(device_name):
    hostname = {}
    hostname['HOSTNAME'] = (device_name)
    vlan_data = get_vlan(device_name)
    swport_vlan = vlan_data[0]
    ent_vlan = vlan_data[1]
    campus_vlan = vlan_data[2]
    #print(vlan_data)
    return render_template("vlan_facts.html", fact=hostname, device_name=device_name, vlan=swport_vlan, vlan1=ent_vlan, vlan2=campus_vlan )

@app.route('/main_core/MAC_facts/<string:device_name>', methods=['GET'])
@login_required
def display_MAC_facts(device_name):
    hostname = {}
    hostname['HOSTNAME'] = (device_name)
    interfaceMACdata = get_MAC(device_name)
    connected_switchports_vlan = interfaceMACdata[0]
    switchport_vlan_MAC = interfaceMACdata[1]
    return render_template("MAC_facts.html", fact=hostname, device_name=device_name, MAC=connected_switchports_vlan, MAC1=switchport_vlan_MAC)

if __name__ == "__main__":
    app.run(host='0.0.0.0')