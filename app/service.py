"""Ingestion validation and correlation orchestration."""
from datetime import datetime
from .models import Event,EventType
from .repository import Repository
from .rules import RuleEngine
class LogSentry:
 def __init__(self,repository:Repository,rules:RuleEngine|None=None):self.repository=repository;self.rules=rules or RuleEngine()
 def normalize(self,value):
  required={'event_id','timestamp','event_type','source_ip'};missing=required-value.keys()
  if missing:raise ValueError('missing fields: '+','.join(sorted(missing)))
  timestamp=value['timestamp'] if isinstance(value['timestamp'],datetime) else datetime.fromisoformat(str(value['timestamp']).replace('Z','+00:00'))
  return Event(event_id=str(value['event_id']),timestamp=timestamp,event_type=EventType(value['event_type']),source_ip=str(value['source_ip']),actor=value.get('actor'),target=value.get('target'),outcome=value.get('outcome'),metadata=value.get('metadata',{}))
 def ingest(self,value):return self.repository.add(self.normalize(value))
 def alerts(self,start=None,end=None):return self.rules.evaluate(self.repository.search(start,end,limit=1000))
