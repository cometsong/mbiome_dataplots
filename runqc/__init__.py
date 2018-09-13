# __all__ = ['app', 'config', 'views', 'db', 'models', 'files']
__version_bits__ = (0, 2, 0)
__version__ = ".".join(map(str,__version_bits__))

import os

from flask import Flask

#~~~~ flask extensions ~~~~
from flask_sqlalchemy import SQLAlchemy
# from flask_autoindex import AutoIndex

#~~~~ runqc app pkgs ~~~~~
from runqc.config import config
from runqc import views

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Flask App Config ~~~~~
def configure_app(app, env=None, test_config:dict={}):
    if not test_config:
        # load the instance config, if it exists, when not testing
        if env:
            app.config.from_object(config[env])
        else:
            app.config.from_object(config['default'])
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


def check_app_config(app):
    """ check the important config vars """
    try:
        if not app.config['SQLALCHEMY_DATABASE_URI']:
            raise ValueError("No database set for application")

        if not app.config['APPLICATION_ROOT']:
            raise ValueError("No application root path for application")

        # instance-specific
        if app.config['ENV'] == "production":
            if not app.config['SECRET_KEY']:
                raise ValueError("No secret key set for app's production session")

    except Exception as e:
        raise e


def configure_extensions(app):
    db = SQLAlchemy()
    db.init_app(app)

    #TODO: def configure_errorhandlers(app) ??
    #TODO: def configure_logging(app) ??

    #TODO: modify css for AutoIndex if using it for run list or fastqc dirs
    # AutoIndex(app, browse_root=app.config['RUN_DATASETS'])


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Create the App ~~~~~
ENV = os.environ.get('FLASK_ENV', 'default')

def create_app(test_config:dict={}):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    configure_app(app, ENV, test_config)
    check_app_config(app)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    app.register_blueprint(views.run_info)

    # configure_extensions(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    # show environ vars
    @app.route('/environ')
    def env_vars():
        from flask import jsonify
        env_items = {k:v for k, v in os.environ.items()}
        app_info = {
                    'name': str(app.name),
                    'root_path': str(app.root_path),
                    'blueprints': str(app.blueprints),
                    'import_name': str(app.import_name),
                    'instance_path': str(app.instance_path),
                    'error_handler_spec': str(app.error_handler_spec),
                   }
        app_config = {k:str(v) for k, v in app.config.items()}

        return jsonify(
            env=env_items,
            app_info=app_info,
            app_config=app_config,
            )

    return app

