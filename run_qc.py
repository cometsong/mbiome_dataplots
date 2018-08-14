import os
from flask import Flask
import config

app = Flask(__name__.split('.')[0])

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Flask App Config ~~~~~
def get_config_obj(env='FLASK_ENV'):
    """get CONFIG from ENV or default to production """
    ENV= os.environ.get(env, None)
    if ENV.lower() in ("devel", "development"):
        conf_obj = 'config.DevelConfig'
    elif ENV.lower() in ("test", "tests", "testing"):
        conf_obj = 'config.TestingConfig'
    else: # production
        conf_obj = 'config.ProductionConfig'
    return conf_obj

app.config.from_object(get_config_obj())

# check the important config vars:
if not app.config['DATABASE_URI']:
    raise ValueError("No database set for Flask application")
if not app.config['APPLICATION_ROOT']:
    raise ValueError("No application root path for Flask application")

# instance-specific
if app.config['ENV'] == "production" and not app.config['SECRET_KEY']:
    raise ValueError("No secret key set for Flask application")


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Routes and Views ~~~~~
@app.route(app.config['APPLICATION_ROOT'])
def run_details():
    """show main page for each run's qc"""
    pass
