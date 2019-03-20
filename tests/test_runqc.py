"""Test base app setup"""

from tests.conftest import _get_response

def test_hello_view(client):
    """test hello world route"""
    url = '/hello'
    data_check = b'Hello, World!'
    (response, *others) = _get_response(client, url)
    assert data_check in response.data


def test_environ_json(client):
    """test environ vars json page"""
    url = '/environ'
    (response, *others) = _get_response(client, url)
    envrn = response.get_json()
    assert envrn['app_config']['ENV'] == 'testing'
    assert envrn['app_config']['APPLICATION_ROOT'] == '/run_qc_testing'

