cd $PWD
. venv/bin/activate
gunicorn --bind 0.0.0.0:5555 wsgi --reload --reload-extra-file $PWD/hosts.yaml