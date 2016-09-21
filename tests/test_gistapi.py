import os
import json
import tempfile

import pytest

import gistapi


@pytest.fixture
def client(request):
    #db_fd, gistapi.app.config['DATABASE'] = tempfile.mkstemp()
    gistapi.app.config['TESTING'] = True
    client = gistapi.app.test_client()

    #with gistapi.app.app_context():
    #    gistapi.init_db()

    #def teardown():
    #    os.close(db_fd)
    #    os.unlink(flaskr.app.config['DATABASE'])
    #request.addfinalizer(teardown)

    return client


def test_ping(client):
    """Start with a sanity check."""
    rv = client.get('/ping')
    assert b'pong' in rv.data


def test_search(client):
    """Start with a passing test."""
    post_data = {'username': 'jorujlu', 'pattern': 'aa'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success',
                     'username': 'jorujlu',
                     'pattern': 'aa',
                     'matches': ['https://gist.github.com/jorujlu/1f95b121c002ec2e997f7ef491d2c15c', 'https://gist.github.com/jorujlu/3d45258e1cae94ffb669175696293bb3']}
    assert result_dict == expected_dict
