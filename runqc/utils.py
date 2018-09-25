import os
import json
from pathlib import PosixPath as Path
from decorator import decorator

from flask import current_app


# modified from: https://stackoverflow.com/a/10961991/1600630
def make_tree(path, recursive=False):
    """ get list of 'path's contents, recursively if desired
    
    To use in template:
    #TODO: get template usage into here!
    
    """
    current_app.logger.debug('make_tree path: %s', path)
    tree = dict(name=path, contents=[])
    lst = ()
    try:
        lst = os.listdir(path)
    except OSError as ose:
        tree = "There was an OSError... {}".format(str(ose))
    except Exception as e:
        tree = "There was an Error... {}".format(str(e))
    else:
        for name in lst:
            fn = os.path.join(path, name)
            if os.path.isdir(fn) and recursive:
                tree['contents'].append(make_tree(fn, recursive=recursive))
            else:
                tree['contents'].append(dict(name=fn))
    return tree


@decorator
def check_run_info_json(func, run_path, *args, **kwargs):
    """view decorator to check for existing file 'run_info.json'
    and create it if not.
    N.B. Expects view first arg = 'run_path'
    """
    # run_path = args[0]
    run = Path(run_path)
    info = run / 'run_info.json'
    try:
        if info.exists():
            txt = info.read_text()
            if '{' in txt:
                run_info = json.loads(txt)
        else:
            run_info = make_json_from_qc_files(run_dir, json_filename)
    except Exception as e:
        raise e
    finally:
        return func(*args, **kwargs)


def read_file_text(filename: Path):
    """return all text contents in line-based array of file or 'None' if not a text file"""
    filename = Path(filename)
    current_app.logger.info('Reading text from file: %s', filename.resolve())
    text_lines = []
    try:
        filename.open()
        text_lines = filename.read_text().splitlines()
        current_app.logger.debug('from %s text_lines[0:1]: %s', filename.name, str(text_lines[0:1]))
        return text_lines

    except Exception as e:
        current_app.logger.error('Errors reading from file: %s!', filename.resolve())
        return None


def get_run_qcreport_data(project_name, run_dir,
                          qcreport_glob='*_QCreport*.csv',
                          qcreport_data_suffix='_QCreport.data.csv'):
    """Return run Qcreport data file if exists,
    else parse the actual data lines after row starting 'GT_QC_Sample_ID'
    """
    run_base = os.path.basename(run_dir)
    current_app.logger.info('Getting QCreport data: %s', run_dir)
    data_header = 'GT_QC_Sample_ID,Sample_Name'
    qcr_lines = []
    qcr_rows = []
    try:
        run_path = Path(run_dir)
        # current_app.logger.debug('qcreport. run_path: %s', run_path)
        qcr_data_file = ''.join([ project_name, qcreport_data_suffix])
        qcr_data_path = os.path.join(run_dir, qcr_data_file)
        # current_app.logger.debug('qcr_data_file: %s', qcr_data_file)
        qc_reports = run_path.glob(qcreport_glob)
        # current_app.logger.debug('qcreports: %s', qc_reports)
        for f in qc_reports:
            if f.match(qcreport_data_suffix):
                current_app.logger.info('QCreport data file found: %s', run_info)
                return f.resolve()
            elif f.is_file():
                qcr_lines = read_file_text(f)

        try:
            for index, row in enumerate(qcr_lines):
                # current_app.logger.debug('qc_report row: %s', str(row[0:30)])
                if data_header in row:
                    qcr_rows = os.linesep.join(qcr_lines[index:])
                    break
            if qcr_rows:
                with open(qcr_data_path, 'w') as qcd:
                    qcd.writelines(qcr_rows)
                    current_app.logger.info('QCreport data now written to file: %s', qcr_data_path)
                with open(qcr_data_path, 'r') as qcd:
                    qcd = qcd.readlines()
                    if len(qcd) == len(qcr_rows):
                        current_app.logger.info('QCreport data successfully read-checked.')
        except Exception as e:
            current_app.logger.error('QCreport data row reading issues: %s', run_dir)
            raise e
    except Exception as e:
        current_app.logger.error('QCreport data file issues: %s', run_dir)
        raise e
    finally:
        return qcr_data_path


def get_run_json(run_dir, json_filename):
    """Parse run json file if exists, else make one from the QC csv files in the run_path"""
    run_info = {'info details': 'not found'}
    try:
        run_path = Path(run_dir)
        run_json = run_path / json_filename
        try:
            run_json.open()
            json_text = run_json.read_text()
            run_info = json.loads(json_text)
        except:
            run_info = make_json_from_qc_files(run_dir, json_filename)
        current_app.logger.info('run_json: %s', run_info)
    except Exception as e:
        raise e
    finally:
        return run_info


def make_json_from_qc_files(dirname: str, json_filename: str):
    """read QC csv files and create run summary in json format"""
    try:
        work_path = Path(dirname).resolve()
        json_file = work_path / json_filename

        info_dict = {}
        qc_info = {}
        metric_info = {}

        qc_report_csv_glob = '*_QCreport*.csv'
        qc_report_fieldnames = \
            [ 'Project', 'Sequence Protocol', 'Sample Size', 'Fastq Files', 'Date Report' ]
        # N.B. line formats of this report are: "Project: 18-weinstock-005,,,,,"

        run_metrics_csv_glob = 'Run_Metric_*.csv'
        run_metrics_field_names = \
            ['RunDate', 'ProjectSeqRequestDate', 'LIMSProjectID', 'LIMSID', 'MachineID',
             'FlowCellID', 'LoadingConc.(pM)', 'Density', 'PF', 'Q30',
             'Reads(M)', 'ReadsPF (M)', 'TotalYield(Gb)', 'PhiXAligned%', 'PHIXLot'
            ]

        current_app.logger.info('Finding QCreport file')
        qc_report_list = list(work_path.glob(qc_report_csv_glob))
        # current_app.logger.debug('qc_report_list: %s', qc_report_list)
        qcr_lines = []
        try:
            qc_report_csv = qc_report_list[0]
            qcr_lines = read_file_text(qc_report_csv)

            qcr_rows = [r.split(',') for r in qcr_lines]
            # current_app.logger.debug('length qcr_rows: %s', len(qcr_rows))

            for row in qcr_rows:
                # current_app.logger.debug('qcr_row: %s', str(row))
                for fld in qc_report_fieldnames:
                    if fld in row[0]:
                        # current_app.logger.debug('fld: %s', fld)
                        [f1, f2] = row[0].replace(',', '').split(': ')
                        # current_app.logger.debug('f1,f2: %s, %s', f1, f2)
                        qc_info.update({f1: f2})
            current_app.logger.debug('qc_info: %s', qc_info)

            info_dict.update(qc_info)
        except Exception as e:
            current_app.logger.error('reading from run''s QCreport csv file!')

        current_app.logger.info('Finding RunMetrics file')
        run_metrics_list = list(work_path.glob(run_metrics_csv_glob))
        current_app.logger.debug('run_metrics_list: %s', run_metrics_list)
        run_metrics_dict = {}
        try:
            run_metrics_csv = run_metrics_list[0]
            with open(run_metrics_csv) as qrm:
                qrm_head = qrm.readline().split(',')
                qrm_data = qrm.readline().split(',')
                run_metrics_dict = dict(zip(qrm_head, qrm_data))

            metric_info = {k:v for k,v in run_metrics_dict.items()
                           if k in run_metrics_field_names}
            current_app.logger.debug('metric_info: %s', metric_info)

            info_dict.update(metric_info)
        except Exception as e:
            current_app.logger.error('reading from run''s Run Metrics csv file!')

    except Exception as e:
        raise e
    
    try:
        current_app.logger.info('Writing info out to json file.')
        try:
            json_file.open(mode='w')
            json_file.write_text(json.dumps(info_dict))
        except:
            current_app.logger.error('json file %s is not writable!', json_file)
    except OSError as e:
        raise e

    return info_dict


def get_file_paths(folder, fileglob="*", name_only=False):
    """pre-check if file(s) exist(s) and return list of Path objects or filenames only"""
    fldr = Path(folder)
    files = []
    try:
        for f in fldr.glob(fileglob):
            current_app.logger.info('get_file_paths dir glob name: %s', f)
            if f.is_file():
                if name_only:
                    files.append(f.name)
                else:
                    files.append(f)
        # current_app.logger.debug('get_file_paths files: %s', str(files))
        return files
    except:
        return False


def check_file_exists(folder, fileglob="*"):
    """pre-check if file(s) exist(s) for links in view templates"""
    fldr = Path(folder)
    try:
        for f in fldr.glob(fileglob):
            current_app.logger.info('checking found fname: %s', f)
            if f.is_file():
                return True
    except:
        return False


def parse_run_name_qc(dirname):
    """parse run name from folder name"""
    run_name = os.path.basename(dirname)
    current_app.logger.debug('run dir for name: %s', dirname)
    if run_name.endswith('/'):
        run_name = run_name[:-1]
    if run_name.endswith('_qc'):
        run_name = run_name[:-3]
    return run_name


