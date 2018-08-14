import os

def get_env_var(varname, default=None):
    """get config var value from ENV"""
    try:
        var_env = os.environ.get(varname, default=default)
        return var_env
    except KeyError as ke:
        raise ke
    except:
        raise


class DefaultConfig(object):
    env = get_env_var
    ENV = env("FLASK_ENV", None)
    DEBUG = env("FLASK_DEBUG", False)
    TESTING = env("TESTING", False)
    SECRET_KEY = env("SECRET_KEY", None)
    DATABASE_URI = env("FLASK_DB", 'sqlite:///:memory:')
    APPLICATION_ROOT = env("FLASK_APP_ROOT", 'run_qc')
    SERVER_NAME = env("FLASK_SERVER_NAME", 'mbiomecore')
    PREFERRED_URL_SCHEME = env("FLASK_PREFERRED_URL", 'https')


class ProductionConfig(DefaultConfig):
    ENV = 'production'
    DEBUG = False
    #TODO: make a prod db (and devel?)
    DATABASE_URI = get_env_var("FLASK_DB", None)


class DevelConfig(DefaultConfig):
    ENV = 'development'
    DEBUG = True
    APPLICATION_ROOT = get_env_var("FLASK_APP_ROOT", "/run_qc_devel/")


class TestingConfig(DefaultConfig):
    ENV = 'testing'
    TESTING = True

