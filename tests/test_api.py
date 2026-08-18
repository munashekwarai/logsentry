from fastapi.testclient import TestClient
from app import api
from app.repository import Repository
from app.service import LogSentry

def client(monkeypatch):
 repo=Repository();monkeypatch.setattr(api,'repository',repo);monkeypatch.setattr(api,'service',LogSentry(repo));return TestClient(api.app)
def payload(id,actor='user@example.test'):return {'event_id':id,'timestamp':'2026-01-01T00:00:00Z','event_type':'auth_failure','source_ip':'192.0.2.4','actor':actor}
def test_ingest_search_statistics_and_alerts(monkeypatch):
 http=client(monkeypatch)
 for i in range(5):
  value=payload(str(i),f'user{i}@example.test');value['timestamp']=f'2026-01-01T00:0{i}:00Z';assert http.post('/events',json=value).status_code==201
 assert http.get('/events?source_ip=192.0.2.4').json()[0]['event_id']=='4';assert http.get('/statistics').json()['total']==5
 rules={x['rule_id'] for x in http.get('/alerts').json()};assert rules=={'AUTH_FAILURE_BURST','PASSWORD_SPRAY'}
def test_duplicate_validation_and_simulation_label(monkeypatch):
 http=client(monkeypatch);assert http.post('/events',json=payload('x')).status_code==201;assert http.post('/events',json=payload('x')).status_code==409
 assert http.post('/events',json={}).status_code==422;sample=http.post('/samples/generate?failures=2').json();assert sample['label']=='SIMULATED SECURITY EVENTS'
