from web import create_app
import sys
import logging
import os
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['FLASK_ENV'] = 'production'
root_path = '/home/truong/Repos/converter'
activate_this = root_path + 'env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, root_path)
os.chdir(root_path + 'web/')

application = create_app()
