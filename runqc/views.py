import os

from flask import Blueprint, make_response, render_template
from flask import current_app, g
# from flask.cli import with_appcontext

# app = current_app

# from runqc import app
# from . import app
from runqc.files import make_tree

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Routes and Views ~~~~~
run_info = Blueprint('run_info', __name__) #, url_prefix='/runs')

# current_app.logger.info("run_qc views!")

# @app.route('/runs', strict_slashes=True)
@run_info.route('/', methods=['GET']) #, defaults={'page': 'index'})
def run_list():
    """show list of run names."""
    datasets = current_app.config['RUN_DATASETS']
    # Note: join with dirname of app.instance_path filename to get disk location.
    # datasets = os.path.join(os.path.dirname(app.instance_path), datasets)
    if not os.path.isabs(datasets):
        datasets = os.path.join(current_app.instance_path, datasets)

    vars = {
        # 'url_prefix': datasets,
        'run_dirs': make_tree(datasets),
    }
    # current_app.logger.debug(f'context: {vars!s}')
    response = make_response(render_template('run_list.html', **vars))
    response.headers['X-Datasets'] = datasets
    response.headers['X-Glorious'] = 'Welcome to Mbiome Core Sequencer Runs!'
    return response

# @run_info.route('/<path:run_path>', strict_slashes=True)
@run_info.route('/<path:run_path>', strict_slashes=True)
def run_details(run_path):
    """show main page for each run's qc
    
    Expected run_path name structure:
      20180725_18-weinstock-004_CCGN5ANXX_qc/
      yyyymmdd [--gt-project--] flowcell _qc
    """
    #TODO: store variables in generated db?
    #TODO: split <run>_QCReport.csv into 'infos.html' and dataTable.csv chunks (sed script? python function?)
    #TODO: put/get project info variables using generated db?

    try:
        if run_path.endswith('_qc'):
            run_name = run_path[:-3]
        else:
            run_name = run_path

        if '_' in run_name:
            path_parts = run_name.split('_')
            if run_name.startswith('\d\d\d\d\d\d\d\d_'): #yyyymmdd_
                import_date = path_parts[0]
            else:
                import_date = ''
            gt_project = path_parts[1]
            try:
                flowcell = path_parts[2]
            except:
                flowcell = ''
        else:
            gt_project = run_name
            import_date = ''
            flowcell = ''

    except Exception as e:
        raise e

    vars = {
        'run_path': run_path,
        'run_name': run_name,
        'gt_project': gt_project,
        'import_date': import_date,
        'flowcell': flowcell,
    }
    # current_app.logger.debug(f'context: {vars!s}')
    response = make_response(render_template('run_qc.html', **vars))
    # response.headers['X-Parachutes'] = 'parachutes are cool'
    return response


# @run_info.route('/<path:run_path>/fastqc_files')
@run_info.route('/<path:run_path>/fastqc_files')
def fastqc_list(run_path):
    """show run's fastqc files"""
    fastqc_path = 'fastqc'
    fastqc_tree = make_tree(os.path.join(run_path, fastqc_path))
    fastqc_files = {}
    vars = {
        'run_path': run_path,
        'fastqc_path': fastqc_path,
        'fastqc_results': fastq_files,
    }
    # current_app.logger.debug(f'context: {vars!s}')
    return render_template('run_fastqc.html', **vars)


# @run_info.route('/runs/<path:run_path>/<path:fastqc_path>/',
@run_info.route('/runs/<path:run_path>/<path:fastqc_path>/',
                defaults={'fastqc_path': 'fastqc'},
                endpoint='fastqc')
# TODO: use 'redirect' for fastqc path ??
def fastqc_path(run_path, fastqc_path):
    """show run's fastqc folder"""
    vars = {
        'run_path': run_path,
        'fastqc_path': fastqc_path,
    }
    # current_app.logger.debug(f'context: {vars!s}')
    return render_template('run_fastqc.html', **vars)


# @run_info.route('/<path:run_path>/fastqc_files')
@run_info.route('/<path:run_path>/pipe_reads')
def run_pipe_reads(run_path):
    """show run's fastqc files"""
    vars = {
        'run_path': run_path,
    }
    return render_template('run_fastqc.html', **vars)

