"""Test views used in app"""
import pytest

from tests.conftest import _get_response
# from tests.conftest import RUN_NAME_TEST

# format: LIST_NAME = [url, data_check[s], ...]
RUN_LIST = ['/', b'<title>Mbiome Core Sequencer Run QC List</title>']
RUN_ITEM = ['/', '<a class="large" href="{}/{}">{}</a>'] # str.encode back to bytes!
RUN_PAGE = ['(url is passed as run_path)',
            '<title>RunQC: {}</title>',
            'MicrobiomeCore Run QC Info for "{}"',
            ]
FQC_LIST = ['/fastqc', b'<h2>FastQC Result List</h2>']
FQC_PAGE = ['/fastqc/Undetermined_S0_R1_001_fastqc.html',
            b'<td>Filename</td><td>Undetermined_S0_R1_001.fastq.gz</td>']


def test_run_list(client):
    """test run list"""
    url = RUN_LIST[0]
    data_check = RUN_LIST[1]
    (response, resphead, respdata, respdict) = _get_response(client, url)
    assert data_check in response.data


def test_run_list_item(app, client, run_path):
    """test run list"""
    url = RUN_ITEM[0]
    runs = app.config['APPLICATION_ROOT']
    # data_check = RUN_ITEM[1].format(runs, RUN_NAME_TEST, RUN_NAME_TEST.replace('_qc','')).encode()
    data_check = RUN_ITEM[1].format(runs, run_path, run_path.replace('_qc','')).encode()
    (response, resphead, respdata, respdict) = _get_response(client, url)
    assert data_check in response.data


def test_run_page(client, run_path):
    """test run page"""
    url = run_path +'/'
    title_check = RUN_PAGE[1].format(run_path.replace('_qc','')).encode()
    header_check = RUN_PAGE[2].format(run_path.replace('_qc','')).encode()
    (response, resphead, respdata, respdict) = _get_response(client, url)
    assert title_check in response.data
    assert header_check in response.data


def test_fastqc(client, run_path):
    """test fastqc main list"""
    url = run_path + FQC_LIST[0]
    data_check = FQC_LIST[1]
    (response, resphead, respdata, respdict) = _get_response(client, url)
    assert data_check in response.data


def test_fastqc_page(client, run_path):
    """test fastqc individual page"""
    url = run_path + FQC_PAGE[0]
    data_check = FQC_PAGE[1]
    (response, resphead, respdata, respdict) = _get_response(client, url)
    assert data_check in response.data


#TODO: test_run_qc_csv
@pytest.mark.skip(reason='Test not implemented yet (CSV files need actual data!)')
def test_run_qc_csv(client, run_path):
    """test run qc csv info"""
    assert "QCreport.csv" == False


#TODO: test_run_json
@pytest.mark.skip(reason='Test not implemented yet (json needs actual data!)')
def test_run_json(client, run_path):
    """test run json info"""
    assert "runinfo.json" == False


#TODO: test_run_stats (average, plus last-10-runs)
@pytest.mark.skip(reason='Stats not implemented yet')
def test_run_stats(client, run_path):
    """test run stats"""
    assert "run_stats" == False


