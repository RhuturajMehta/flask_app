cd $PWD
mkdir Buildings
npm init -y
npm install jquery@1.9.1
npm install @popperjs/core
npm install popper.js@^1.16.1
npm install bootstrap@4.5.2
npm audit fix --force
mv package.json static
mv package-lock.json static
mv node_modules static
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip3 install -r requirements.txt
chmod 755 start_app_dev.sh
chmod 755 start_app_prod.sh

