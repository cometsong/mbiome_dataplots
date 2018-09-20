"""
WSGI for run_qc project.
"""
import os
from os.path import join as pjoin
from collections import OrderedDict

import sys
sys.stdout = sys.stderr

# virtualenv dir variables
app_root = os.path.abspath(os.path.dirname(__file__))
dirs = OrderedDict(
    sitepkgs = pjoin(app_root, 'venv', 'lib/python3.6/site-packages'),
    venv_bin = pjoin(app_root, 'venv', 'bin'),
    venv_dir = pjoin(app_root, 'venv'),
    app_path = pjoin(app_root, 'runqc'),
    app_root = app_root,
)
for d in dirs.values():
    os.environ["PATH"] = ':'.join([d, os.environ["PATH"]])
    sys.path.insert(0, d)

# print(f'DEBUG sys.path: {sys.path!s}')
# print(f'DEBUG path: {os.environ.get("PATH")}')

### set all ENV vars for app to run
# including some from instance_wrapper or cli
os.environ["FLASK_APP"] = 'runqc'
os.environ["FLASK_ENV"] = 'production'
os.environ["FLASK_DEBUG"] = 'False'

# check dirname for devel instance
print(f'app_root: {app_root}')
if 'devel' in app_root:
    os.environ["FLASK_APP_ROOT"] = '/run_qc_devel'
    os.environ["FLASK_ENV"] = 'development'
    os.environ["FLASK_DEBUG"] = 'True'


from runqc import create_app
application = create_app()

if __name__ == '__main__':
    application.logger.info('run_qc is loaded!')
    application.run(host='0.0.0.0', port=443,
                    debug=os.environ["FLASK_DEBUG"])

