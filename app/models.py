"""Normalized security event and alert models."""
from __future__ import annotations
from dataclasses import asdict,dataclass,field
from datetime import datetime,timezone
from enum import StrEnum
from ipaddress import ip_address
from typing import Any
class EventType(StrEnum): AUTH_FAILURE='auth_failure';AUTH_SUCCESS='auth_success';PRIVILEGE_CHANGE='privilege_change';API_REQUEST='api_request'
class Severity(StrEnum): LOW='LOW';MEDIUM='MEDIUM';HIGH='HIGH';CRITICAL='CRITICAL'
@dataclass(frozen=True,slots=True)
class Event:
 event_id:str;timestamp:datetime;event_type:EventType;source_ip:str;actor:str|None=None;target:str|None=None;outcome:str|None=None;metadata:dict[str,Any]=field(default_factory=dict);id:int|None=None
 def __post_init__(self):
  if not self.event_id.strip() or len(self.event_id)>128:raise ValueError('event_id must contain 1 to 128 characters')
  if self.timestamp.tzinfo is None:raise ValueError('timestamp must include a timezone')
  ip_address(self.source_ip)
  if self.actor is not None and len(self.actor)>254:raise ValueError('actor is too long')
  if len(str(self.metadata))>8192:raise ValueError('metadata is too large')
 def to_dict(self):
  value=asdict(self);value['timestamp']=self.timestamp.astimezone(timezone.utc).isoformat();value['event_type']=self.event_type.value;return value
@dataclass(frozen=True,slots=True)
class Alert:
 rule_id:str;title:str;severity:Severity;source_ip:str;window_start:datetime;window_end:datetime;evidence_count:int;summary:str;event_ids:tuple[str,...]
 def to_dict(self):
  value=asdict(self);value['severity']=self.severity.value;value['window_start']=self.window_start.isoformat();value['window_end']=self.window_end.isoformat();value['event_ids']=list(self.event_ids);return value
