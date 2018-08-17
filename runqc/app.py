import os

from flask import Flask
from flask import make_response, render_template, request

import config


app = Flask(__name__.split('.')[0],
            # template_folder='./runqc/templates',
            static_url_path='/static',
            static_folder='/var/www/html/static',
            )

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Flask App Config ~~~~~
def get_config_obj(env='FLASK_ENV'):
    """get CONFIG from ENV or default to production """
    ENV = os.environ.get(env, None)
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

url_root = app.config['APPLICATION_ROOT']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Routes and Views ~~~~~
app.logger.info("run_qc views!")
@app.route('/')
def hello():
    return "hello app!\n"

@app.route(url_root)
@app.route(url_root+'/')
def run_list():
    """show list of runs"""
    return make_response(render_template('run_list.html'))

# index = run_list

@app.route(url_root+'/<run_path>')
@app.route(url_root+'/<run_path>'+'/')
def run_details(run_path):
    """show main page for each run's qc"""
    #TODO: store variables in generated json file?
    #TODO: store variables in generated db?

    # expected run_path name structure:
    #   20180725_18-weinstock-004_CCGN5ANXX_qc/
    #   yyyymmdd [--gt-project--] flowcell _qc
    try:
        if '_' in run_path:
            if run_path.endswith('_qc'):
                run_name = run_path[:-3]
            path_parts = run_path.split('_')
            if run_path.startswith('\d\d\d\d\d\d\d\d_'): #yyyymmdd_
                import_date = path_parts[0]
            gt_project = path_parts[1]
            flowcell = path_parts[2]
        else:
            run_name = run_path
            gt_project = run_path

    except Exception as e:
        raise e


    vars = {
        'run_name': run_name,
        'gt_project': gt_project,
    }
    app.logger.debug(f'context: {vars!s}')
    response = make_response(render_template('run_qc.html', **vars))
    # response.headers['X-Parachutes'] = 'parachutes are cool'
    return response


# if __name__ == '__main__':
    # app.run()

