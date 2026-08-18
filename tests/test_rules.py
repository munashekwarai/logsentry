from datetime import datetime,timedelta,timezone
import pytest
from app.generator import SIMULATED_LABEL,generate
from app.models import EventType,Severity
from app.repository import DuplicateEventError,Repository
from app.rules import RuleEngine
from app.service import LogSentry

def event(id,kind='auth_failure',ip='192.0.2.3',actor='user@example.test',seconds=0):return {'event_id':id,'timestamp':(datetime(2026,1,1,tzinfo=timezone.utc)+timedelta(seconds=seconds)).isoformat(),'event_type':kind,'source_ip':ip,'actor':actor,'metadata':{}}
def test_normalization_rejects_missing_invalid_ip_and_naive_time():
 service=LogSentry(Repository())
 with pytest.raises(ValueError,match='missing'):service.ingest({})
 with pytest.raises(ValueError):service.ingest(event('x',ip='not-an-ip'))
 value=event('x');value['timestamp']='2026-01-01T00:00:00'
 with pytest.raises(ValueError,match='timezone'):service.ingest(value)
def test_repository_deduplicates_and_filters_events():
 repo=Repository();service=LogSentry(repo);service.ingest(event('a'));service.ingest(event('b',kind='api_request',ip='198.51.100.1'))
 with pytest.raises(DuplicateEventError):service.ingest(event('a'))
 assert [x.event_id for x in repo.search(event_type=EventType.API_REQUEST)]==['b'];assert repo.stats()=={'total':2,'by_type':{'api_request':1,'auth_failure':1},'unique_sources':2,'window_start':None,'window_end':None}
def test_repeated_failures_and_password_spray_correlate_evidence():
 service=LogSentry(Repository(),RuleEngine(auth_limit=5,spray_users=4))
 for i in range(6):service.ingest(event(str(i),actor=f'user{i}@example.test',seconds=i*20))
 alerts=service.alerts();assert [x.rule_id for x in alerts[:2]]==['PASSWORD_SPRAY','AUTH_FAILURE_BURST'];assert alerts[0].severity is Severity.CRITICAL;assert alerts[0].evidence_count==6
def test_privilege_change_and_volume_rules_are_independent():
 service=LogSentry(Repository(),RuleEngine(volume_limit=4))
 for i in range(4):service.ingest(event(str(i),kind='api_request',seconds=i))
 service.ingest(event('p',kind='privilege_change',ip='198.51.100.8'))
 rules={x.rule_id for x in service.alerts()};assert rules=={'EVENT_VOLUME_SPIKE','PRIVILEGE_CHANGE'}
def test_events_outside_window_do_not_form_auth_burst():
 service=LogSentry(Repository(),RuleEngine(auth_limit=3,window_minutes=5))
 for i in range(3):service.ingest(event(str(i),seconds=i*400))
 assert service.alerts()==[]
def test_generator_is_deterministic_and_labelled():
 a=generate(datetime(2026,1,1,tzinfo=timezone.utc),seed=7);b=generate(datetime(2026,1,1,tzinfo=timezone.utc),seed=7)
 assert a==b;assert all(x['metadata']['label']==SIMULATED_LABEL for x in a)
