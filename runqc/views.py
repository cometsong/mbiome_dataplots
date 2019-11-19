import os

from flask import Blueprint, current_app
from flask import make_response, render_template, redirect, send_from_directory

from runqc.pipe_qc_plots import (
    plot_16S_read_counts,
    plot_spike_pcts,
)
from runqc.utils import \
    make_tree, \
    get_run_info_json, \
    make_run_json_from_qc_files, \
    get_run_qcreport_data, \
    get_file_paths, \
    parse_run_name_qc, \
    delimited_to_dict

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Routes and Views ~~~~~
run_info = Blueprint('run_info', __name__) #, url_prefix='/runs')

@run_info.route('/', methods=['GET']) #, defaults={'page': 'index'})
def run_list():
    """show list of run names."""
    datasets = current_app.config['RUN_DATASETS']
    url_root = current_app.config['APPLICATION_ROOT']

    run_dirs = {}
    run_dir_list = make_tree(datasets)
    for folder in run_dir_list['contents']:
        # current_app.logger.debug('run_list folder: %s', folder)
        (name, path) = folder.popitem()
        name = path.replace(datasets, '').rstrip('_qc')
        if '/' in name:
            name = name.replace('/', '')
        href = path.replace(datasets, url_root)
        run_dirs.update({name: href})

    vars = {
        'datasets': datasets,
        'run_dirs': run_dirs
    }
    # current_app.logger.debug('context: %s', vars)
    response = make_response(render_template('run_list.html', **vars))
    response.headers['X-Datasets'] = datasets
    response.headers['X-Glorious'] = 'Welcome to Mbiome Core Sequencer Runs!'
    return response


# @run_info.route('/<path:run_path>/(<subitem>.+)?', defaults={'subitem': ''})
@run_info.route('/<path:run_path>/', strict_slashes=True, defaults={'subitem': ''})
@run_info.route('/<path:run_path>/<path:subitem>')
# @check_run_info_json(run_path)
def run_details(run_path, subitem=''):
    current_app.logger.info('Getting details for %s', run_path)
    run_json = 'run_info.json'
    run_abspath = os.path.join(
                  current_app.config['RUN_DATASETS'],
                  run_path)
                  # os.path.dirname(current_app.config['RUN_DATASETS']),
    # current_app.logger.debug('run_abspath: %s', run_abspath)

    try:
        # Snag that subitem time!
        if subitem:
            current_app.logger.info('Getting details for subitem: %s', subitem)
            if subitem.endswith('/'):
                pathtype = 'folder'
                # current_app.logger.debug('subitem type: %s', pathtype)
                # TODO: check existence of folder before servinf empty template!
            else:
                pathtype = 'file'
                # current_app.logger.debug('subitem type: %s', pathtype)

                # current_app.logger.debug('checking subitem suffix: %s %s', run_path, subitem)
                suffixes_as_attachment = ('.xlsx', '.xls', '.csv', '.tsv')
                # suffixes_not_attachment = ( '.png', '.jeg', '.csv' )
                attach = False
                if subitem.endswith(suffixes_as_attachment):
                    attach = True
                return send_from_directory(run_abspath, subitem,
                                           as_attachment=attach)

    except Exception as e:
        current_app.logger.exception('testing subitem types %s %s', run_path, subitem)

    try:
        run_name = parse_run_name_qc(run_path)
        if '_' in run_name:
            path_parts = run_name.split('_')
            try:    gt_project = path_parts[1]
            except: gt_project = ''
            try:    flowcell = path_parts[2]
            except: flowcell = ''
        else: # unexpected folder name structure
            gt_project = run_name
            flowcell = ''

        # load sequencer core's run info from json or make it
        try:
            current_app.logger.info('Getting run_info from: %s / %s', run_abspath, run_json)
            info_json = get_run_info_json(run_abspath, run_json)

            # check if pre-existing before reading both QC files...
            if 'FlowCell ID' not in info_json \
            or 'GT Project' not in info_json:
                info_json = make_run_json_from_qc_files(run_abspath, run_json)
            # update values:
            if 'FlowCellID' in info_json:
                current_app.logger.info('Getting flowcell from run_info')
                flowcell = info_json['FlowCellID']
            if 'LIMSProjectID' in info_json:
                info_json['GT Project'] = info_json.pop('LIMSProjectID')
            if 'GT Project' in info_json:
                current_app.logger.info('Getting gt_project from run_info')
                gt_project = info_json['GT Project']

        except Exception as e:
            current_app.logger.exception('JSON issues...')

        try:
            qcreport_data = get_run_qcreport_data(gt_project, run_abspath)
        except Exception as e:
            qcreport_data = None
            current_app.logger.exception('issues reading QCreport data for run: %s', run_path) #TODO: is 'run_path var type 'Path' ??

        # check if files being linked to exist (yet)
        run_metric_csv = get_file_paths(run_abspath, 'Run_Metric_*.csv', name_only=True)
        if run_metric_csv: run_metric_csv = run_metric_csv[0]

        read_count_sheets = get_file_paths(run_abspath,
                                '[Ss]amples_[Rr]ead_[Cc]ount*.*', name_only=True)
        read_dist_images = get_file_paths(run_abspath,
                                '*_Read_Distributions.png', name_only=True)
        read_dist_images.extend(get_file_paths(run_abspath,
                                'raw_read_distribution_plot*.png', name_only=True))

        fastqc_stats = get_file_paths(run_abspath, 'fastqc_stats.tsv')
        if fastqc_stats:
            fastqc_stats = delimited_to_dict(fastqc_stats[0])
        else:
            fastqc_stats = None
        # current_app.logger.debug(f'fastq_stats: {fastqc_stats}')

        # check for control assemblies accuracies
        control_assems = {}

        flash_stats = get_file_paths(run_abspath, 'flash_stats.tsv')
        if flash_stats:
            flash_stats = delimited_to_dict(flash_stats[0])
            control_assems['flash_stats'] = flash_stats

        flash_accuracy_img = get_file_paths(run_abspath,
                             'flash_assembly_accuracy_plot.png', name_only=True)
        if flash_accuracy_img:
            flash_accuracy_img = flash_accuracy_img[0]
            control_assems['flash_plot'] = flash_accuracy_img

        pear_stats = get_file_paths(run_abspath, 'pear_stats.tsv')
        if pear_stats:
            pear_stats = delimited_to_dict(pear_stats[0])
            control_assems['pear_stats'] = pear_stats

        pear_accuracy_img = get_file_paths(run_abspath,
                            'pear_assembly_accuracy_plot.png', name_only=True)
        if pear_accuracy_img:
            pear_accuracy_img = pear_accuracy_img[0]
            control_assems['pear_plot'] = pear_accuracy_img

        # check for 16S QC read counts
        try:
            pipe_16S_qc_plots = plot_16S_read_counts(run_abspath, flowcell)
        except Exception as e:
            current_app.logger.exception('issues plotting bar charts for run: %s', run_path)

        # check for 16S samples' percent spike reads
        try:
            # Zymo Spikes:  OTU_Allobacillus  OTU_Trupera  OTU_Imtechella
            #FIXME: provide compare_column names in ENV? in config? each run's info? NOT hardcoded!!
            # spikes_compare_cols = current_app.config['PIPELINE_SPIKES_COMPARE_COLUMNS']
            pipe_16S_spike_pcts = plot_spike_pcts(run_abspath)
        except Exception as e:
            current_app.logger.exception('issues plotting charts for run spike reads: %s', run_path)

    except Exception as e:
        current_app.logger.exception('issues generating run_details: %s', run_path)
        raise e

    vars = {
        'run_spec': info_json,
        'run_path': run_path,
        'run_abspath': run_abspath,
        'run_name': run_name,
        'gt_project': gt_project,
        'fastqc_stats': fastqc_stats,
        'qcreport_data': qcreport_data,
        'run_metric_csv': run_metric_csv,
        'read_count_sheets': read_count_sheets,
        'read_dist_images': read_dist_images,
        'control_assems': control_assems,
        'pipe_16S_qc_plots': pipe_16S_qc_plots,
        'pipe_16S_spikes': pipe_16S_spike_pcts,
    }
    # current_app.logger.debug('context: %s', vars)
    response = make_response(render_template('run_details.html', **vars))
    # response.headers['X-Parachutes'] = 'parachutes are cool'
    return response


@run_info.route('/<path:run_path>/fastqc/',
                defaults={'subitem': 'files'}
                )
@run_info.route('/<path:run_path>/fastqc/<subitem>', strict_slashes=True,)
def fastqc_list(run_path, subitem='files'):
    """show list of links to run's fastqc html files"""
    fastqc_path = 'fastqc'

    datasets = current_app.config['RUN_DATASETS']
    fqc_abspath = os.path.join(datasets, str(run_path), fastqc_path)

    if subitem.endswith('.html'):
        return send_from_directory(fqc_abspath, subitem, as_attachment=False)
    if subitem.endswith('.zip'):
        return send_from_directory(fqc_abspath, subitem, as_attachment=True)

    fastqc_files = {}
    try:
        fastqc_tree = make_tree(fqc_abspath)
        for item in fastqc_tree['contents']:
            # Pcurrent_app.logger.debug('fastqc item: %s', item)
            (key, path) = item.popitem()
            name = href = base = os.path.basename(path)
            if not name.endswith('.html'):
                continue
            name = name.rstrip('.html')
            name = name.rstrip('_fastqc')
            fastqc_files.update({name: href})
    except Exception as e:
        current_app.logger.error('List of fastqc files issues: %s', run_path)

    run_name = parse_run_name_qc(run_path)
    vars = {
        'run_path': run_path,
        'run_name': run_name,
        'fastqc_path': fastqc_path,
        'fastqc_files': fastqc_files,
    }
    # current_app.logger.debug('context: %s', vars)
    return render_template('run_fastqc.html', **vars)


# TODO: use 'redirect' for fastqc path ??
### @run_info.route('/<path:run_path>/fastqc/')
def fastqc_path(run_path):  #, fastqc_path):
    """browse run's fastqc folder"""
    location = url_for('run_info.fastqc_list', subitem='all')
    return redirect(location, code=302)


# @run_info.route('/<path:run_path>/pipe_reads')
def run_pipe_reads(run_path):
    """show run's pipeline results"""
    vars = {
        'run_path': run_path,
    }
    return render_template('run_pipe_reads.html', **vars)


# @run_info.route('/<path:run_path>/<subpath>') #, strict_slashes=True)
def run_sub_path(run_path, sub_path):
    """show run sub path"""
    msg = f'view "run_sub_path" with args({run_path}, {sub_path})'
    vars = {
        'run_path': run_path,
        'sub_path': sub_path,
    }
    # return render_template('default.html', **vars)
    return f'This page is going with {msg}', 404

