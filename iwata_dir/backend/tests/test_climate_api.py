"""HTTP integration keeps fixed analyses readable across source loss and work."""
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from fastapi.testclient import TestClient

from backend.app import create_app
from backend.tests.test_climate import create_fixture
from backend.worker import source_snapshot


def test_climate_fixed_http_result_restores_without_source(tmp_path):
    database = tmp_path / 'source.duckdb'
    create_fixture(database)
    state = tmp_path / 'state'
    with TestClient(create_app(state, climate_options={'source_path': database})) as client:
        descriptor = client.get('/api/v1/climate-sources').json()['sources'][0]
        body = {'client_request_id': 'http-1', 'query': {
            'source_id': descriptor['source_id'], 'level_id': 0, 'bounds': None, 'grain': 'half'}}
        result = client.post('/api/v1/climate-analyses', json=body)
        assert result.status_code == 201
        artifact = result.json()
        assert client.post('/api/v1/climate-analyses', json=body).json() == artifact
        conflict = {**body, 'query': {**body['query'], 'level_id': 1}}
        assert client.post('/api/v1/climate-analyses', json=conflict).status_code == 409
        invalid = {**body, 'path': str(database)}
        assert client.post('/api/v1/climate-analyses', json=invalid).status_code == 422
        saved = client.get('/api/v1/project').json()
        saved['project']['ui_state'] = {'weather_real': {
            'schema': 'balloon.climate-view/1', 'applied': {
                'analysis_id': artifact['analysis_id'], 'result_hash': artifact['result_hash']}}}
        assert client.put('/api/v1/project', json={
            'expected_revision': saved['revision'], 'project': saved['project']}).status_code == 200
        assert 'backend/climate/source.py' in source_snapshot()['files']
        assert 'backend/climate/service.py' in source_snapshot()['files']
    # Startup without the original source never creates a synthetic replacement.
    with TestClient(create_app(state, climate_options={})) as client:
        assert client.get('/api/v1/climate-sources').json()['sources'] == []
        assert client.get('/api/v1/climate-analyses/' + artifact['analysis_id']).json() == artifact
        assert client.post('/api/v1/climate-analyses', json=body).json() == artifact
        assert client.post('/api/v1/climate-analyses', json={**body, 'client_request_id': 'new'}).status_code == 503
        restored = client.get('/api/v1/project').json()['project']['ui_state']['weather_real']['applied']
        assert restored['analysis_id'] == artifact['analysis_id']
        assert client.get('/api/v1/health').json()['status'] == 'ok'


def test_climate_aggregation_does_not_block_fixed_get_or_project(tmp_path, monkeypatch):
    database = tmp_path / 'source.duckdb'
    create_fixture(database)
    app = create_app(tmp_path / 'state', climate_options={'source_path': database})
    with TestClient(app) as client:
        source = client.get('/api/v1/climate-sources').json()['sources'][0]
        body = {'client_request_id': 'first', 'query': {'source_id': source['source_id'], 'level_id': 0}}
        artifact = client.post('/api/v1/climate-analyses', json=body).json()
        entered, release = Event(), Event()
        original = app.state.service.climate._source.query
        def blocked(query):
            entered.set()
            assert release.wait(15), 'test must release its artificial pause'
            return original(query)
        monkeypatch.setattr(app.state.service.climate._source, 'query', blocked)
        with ThreadPoolExecutor(max_workers=2) as pool:
            future = pool.submit(client.post, '/api/v1/climate-analyses', json={
                'client_request_id': 'second', 'query': {**body['query'], 'level_id': 1}})
            try:
                assert entered.wait(10)
                def reads():
                    fixed = client.get('/api/v1/climate-analyses/' + artifact['analysis_id'])
                    project = client.get('/api/v1/project')
                    return fixed, project
                fixed, project = pool.submit(reads).result(timeout=5)
                assert fixed.json() == artifact and project.status_code == 200
            finally:
                release.set()
            assert future.result(timeout=10).status_code == 201
