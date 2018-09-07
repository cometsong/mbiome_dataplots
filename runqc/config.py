import sys
import os
from os.path import abspath, join as pjoin, curdir, dirname, isdir

root_path = abspath(dirname(__file__))


def get_env(varname, default=None):
    """get config var value from ENV"""
    try:
        var_env = os.environ.get(varname, default=default)
    except KeyError as ke:
        raise ke
    except:
        raise
    else:
        return var_env


class Config(object):
    ENV = get_env("FLASK_ENV", None)
    DEBUG = get_env("FLASK_DEBUG", "False")
    TESTING = get_env("FLASK_TESTING", "False")
    SECRET_KEY = get_env("SECRET_KEY", 'A Secret Adventure!')
    APPLICATION_ROOT = None # NB: must declare in subclasses!
    PREFERRED_URL_SCHEME = get_env("FLASK_PREFERRED_URL", 'https')

    SQLALCHEMY_DATABASE_URI = get_env("FLASK_DB_URI",
        'sqlite:///' + pjoin(root_path, 'runqc_data.sqlite'))
    SQLALCHEMY_TRACK_MODIFICATIONS = "False"
    SQLALCHEMY_RECORD_QUERIES = "False"
    SQLALCHEMY_ECHO = "False"
    DB_SCHEMA = get_env("FLASK_DB_SCHEMA", pjoin(root_path, 'dbschema.sql'))

    # TODO: use absolute path of datasets!?
    RUN_DATASETS = get_env("FLASK_APP_RUN_DATASETS", 'runs')
    # if not RUN_DATASETS.startswith('/'):
    #     RUN_DATASETS = .... What shall I join it with???
    #     datasets = pjoin(dirname(app.instance_path), datasets)


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = "False"
    APPLICATION_ROOT = get_env("FLASK_APP_ROOT", '/run_qc')

    try: # SECRET_KEY
        secret_file = pjoin(dirname(root_path), 'secret_production.key')
        secret_read = open(secret_file, 'rb').read()
        SECRET_KEY = get_env("SECRET_KEY", secret_read)
    except IOError:
        print('Error: No secret key. Create it with:')
        if not isdir(dirname(secret_file)):
            print('mkdir -p', dirname(secret_file))
        print('head -c 24 /dev/urandom >', secret_file)
        sys.exit(1)

    from runqc.db import db_config
    SQLALCHEMY_DATABASE_URI = db_config['url']
    SQLALCHEMY_RECORD_QUERIES = "False"


class DevelConfig(Config):
    ENV = 'development'
    DEBUG = "True"
    SQLALCHEMY_RECORD_QUERIES = "True"
    SQLALCHEMY_ECHO = "True"
    APPLICATION_ROOT = get_env("FLASK_APP_ROOT", "/run_qc_devel")


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = "True"
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_RECORD_QUERIES = "True"
    SQLALCHEMY_ECHO = "True"
    APPLICATION_ROOT = get_env("FLASK_APP_ROOT", "/run_qc_testing")


config = {
    'development': DevelConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelConfig
}
