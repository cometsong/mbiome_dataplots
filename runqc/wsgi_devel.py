"""
WSGI config for run_qc project.
"""
# semi-global wsgi script
import os
import sys
sys.stdout = sys.stderr

# virtualenv variables
venv_dir = "/var/www/apps/run_qc_devel" # devel app
path_app = venv_dir + "/runqc"
path_site_packages = venv_dir + "/lib/python3.6/site-packages"

### set all ENV vars for app to run
os.environ["FLASK_APP"] = "runqc:app"
os.environ["FLASK_ENV"] = "development" # devel app
os.environ["FLASK_DEBUG"] = "True"      # devel app

os.environ["PATH"] = path_site_packages + ":" + os.environ["PATH"]
os.environ["PATH"] = venv_dir+"/bin" + ":" + os.environ["PATH"]
os.environ["PATH"] = path_app + ":" + os.environ["PATH"]

### Make sure virtual env is first in sys.path
sys.path.insert(0, path_site_packages)
sys.path.insert(0, path_app)

from .app import app

if __name__ == '__main__':
    app.logger.info("run_qc DEVEL is loaded!") # devel app
    app.run(host='0.0.0.0', port=443,
            debug=os.environ["FLASK_DEBUG"])
