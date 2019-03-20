"""Test all units and fun-bits in app!
This file holds fixture configurations and definitions.
"""
import os
from pathlib import Path

import pytest

from runqc import create_app, configure_app

RUN_NAME_TEST = '20180101_18-microbe-999_TESTY_qc'

FASTQC_HTML_CONTENTS = """
<html>
<body>
    <div class="header">
    <div id="header_title"><img src="" alt="FastQC">FastQC Report</div>
    <div id="header_filename">Mon 01 Jan 2018<br>Undetermined_S0_R1_001.fastq.gz</div>
    </div>
    <h2>Basic Statistics</h2>
    <table><thead><tr><th>Measure</th><th>Value</th></tr></thead>
    <tbody><tr><td>Filename</td><td>Undetermined_S0_R1_001.fastq.gz</td></tr></tbody>
    </table>
</body>
</html>
"""

@pytest.fixture
def app():
    """create and configure a new app instance; fixture for tests"""
    app = create_app()
    configure_app(app, env='testing')
    yield app


@pytest.fixture
def client(app):
    """faux web client; fixture for tests"""
    client = app.test_client()
    yield client


@pytest.fixture
def run_path(app):
    """deliver run_name folder path; fixture for tests
    Prerun of this fixture, ensure actual file paths exist.
    Return URL of run_path.
    """
    runs = app.config['RUN_DATASETS']
    run_name = RUN_NAME_TEST
    runs_path = Path(runs)
    run_path = runs_path / run_name
    create_files(run_path)
    yield run_path.name


def create_files(run_path):
    """create all files in run_path if not pre-existing"""
    run_path.mkdir(parents=True, exist_ok=True)
    run_parts = run_path.name.split('_') # presumes GT-core dept's run-naming w/ '_'
    gt_run_id = run_parts[1] # second chunk after datestamp
    subpaths = [
        'fastqc/Undetermined_S0_R1_001_fastqc.html',
        'fastqc/Undetermined_S0_R1_001_fastqc.zip',
        'Run_Metric_Summary_'+gt_run_id+'.csv',
        gt_run_id+'_QCreport.csv',
        'run_info.json',
    ]
    for subp in subpaths:
        try:
            sub = run_path / subp
            sub_contents = str(sub.resolve())
            if 'Undetermined_S0_R1_001_fastqc.html' == sub.name:
                sub_contents = FASTQC_HTML_CONTENTS
            if not sub.exists():
                try:
                    sub.touch(exist_ok=True)
                except FileNotFoundError:
                    sub.parents[0].mkdir(parents=True, exist_ok=True)
                    sub.touch(exist_ok=True)
                finally:
                    sub.open('w').write(sub_contents)
            # print(f'Run file {sub.resolve()!s} exists')
        except Exception as e:
            raise e


def _get_response(client, url, **kwargs):
    """boilerplate chunk of test"""
    redirects = kwargs.pop('follow_redirects', True)
    response = client.get(url, follow_redirects=redirects, **kwargs)
    resphead = response.headers
    respdata = response.data
    respdict = response.__dict__
    return (response, resphead, respdata, respdict)
    # return (response, resphead, respdata)


