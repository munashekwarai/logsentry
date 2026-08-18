"""Compatibility functions backed by normalized models and the rule engine."""
from .models import EventType
from .service import LogSentry
from .repository import Repository

def normalize(value):return LogSentry(Repository()).normalize(value).to_dict()
def detect(events,window_minutes=5,failure_limit=5,volume_limit=20):
 from .rules import RuleEngine
 service=LogSentry(Repository(),RuleEngine(failure_limit,4,volume_limit,window_minutes))
 for event in events:
  value=dict(event);value.setdefault('event_id',f"legacy-{len(service.repository.search(limit=1000))}");service.ingest(value)
 return [x.to_dict() for x in service.alerts()]
def stats(events):
 service=LogSentry(Repository())
 for event in events:
  value=dict(event);value.setdefault('event_id',f"legacy-{len(service.repository.search(limit=1000))}");service.ingest(value)
 return service.repository.stats()['by_type']
