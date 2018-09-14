import os
from pathlib import PosixPath as Path
import json
from decorator import decorator


# modified from: https://stackoverflow.com/a/10961991/1600630
def make_tree(path, recursive=False):
    """ get list of 'path's contents, recursively if desired
    
    To use in template:
    #TODO: get template usage into here!
    
    """
    print(f"DEBUG make_tree path: {path}")
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
        print(f'run_json: {run_info!s}')
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

        qc_report_csv_glob = '*QCreport*.csv'
        qc_report_fieldnames = \
            [ 'Project', 'Sequence Protocol', 'Sample Size', 'Fastq Files', 'Date Report' ]
        # N.B. line formats of this report are: "Project: 18-weinstock-005,,,,,"

        run_metrics_csv_glob = 'Run_Metric_*.csv'
        run_metrics_field_names = \
            ['RunDate', 'ProjectSeqRequestDate', 'LIMSProjectID', 'LIMSID', 'MachineID',
             'FlowCellID', 'LoadingConc.(pM)', 'Density', 'PF', 'Q30',
             'Reads(M)', 'ReadsPF (M)', 'TotalYield(Gb)', 'PhiXAligned%', 'PHIXLot'
            ]

        print(f'reading QCreport file')
        qc_report_list = list(work_path.glob(qc_report_csv_glob))
        print(f'DEBUG: qc_report_list: {qc_report_list!s}')
        qcr_lines = []
        try:
            qc_report_csv = qc_report_list[0]
            qc_report_csv.open()
            qcr_lines = qc_report_csv.read_text().splitlines()
            # print(f'DEBUG: qcr_lines: {qcr_lines[0:1]!s}')

            qcr_rows = [r.split(',') for r in qcr_lines]
            # print(f'DEBUG: length qcr_rows: {len(qcr_rows)!s}')

            for row in qcr_rows:
                # print(f'DEBUG: qcr_row: {row!s}')
                for fld in qc_report_fieldnames:
                    if fld in row[0]:
                        # print(f'DEBUG: fld: {fld!s}')
                        [f1, f2] = row[0].replace(',', '').split(': ')
                        print(f'DEBUG: f1,f2: {f1!s}, {f2!s}')
                        qc_info.update({f1: f2})
            print(f'DEBUG: qc_info: {qc_info!s}')

            info_dict.update(qc_info)
        except Exception as e:
            print(f'Errors reading from run''s QCreport csv file!')

        print(f'reading RunMetrics file')
        run_metrics_list = list(work_path.glob(run_metrics_csv_glob))
        print(f'DEBUG: run_metrics_list: {run_metrics_list!s}')
        run_metrics_dict = {}
        try:
            run_metrics_csv = run_metrics_list[0]
            with open(run_metrics_csv) as qrm:
                qrm_head = qrm.readline().split(',')
                qrm_data = qrm.readline().split(',')
                run_metrics_dict = dict(zip(qrm_head, qrm_data))

            metric_info = {k:v for k,v in run_metrics_dict.items()
                           if k in run_metrics_field_names}
            print(f'DEBUG: metric_info: {metric_info!s}')

            info_dict.update(metric_info)
        except Exception as e:
            print(f'Errors reading from run''s Run Metrics csv file!')

    except Exception as e:
        raise e
    
    try:
        print(f'Writing info out to json file.')
        try:
            json_file.open(mode='w')
            json_file.write_text(json.dumps(info_dict))
        except:
            print(f'json file {json_file} is not writable!')
    except OSError as e:
        raise e

    return info_dict

