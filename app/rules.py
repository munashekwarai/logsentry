"""Deterministic defensive correlation rules."""
from collections import defaultdict
from datetime import datetime,timedelta,timezone
from .models import Alert,Event,EventType,Severity

def _window_groups(events,minutes):
 ordered=sorted(events,key=lambda x:x.timestamp);groups=[]
 for index,event in enumerate(ordered):
  end=event.timestamp+timedelta(minutes=minutes);group=[x for x in ordered[index:] if x.timestamp<=end]
  groups.append(group)
 return groups
class RuleEngine:
 def __init__(self,auth_limit=5,spray_users=4,volume_limit=30,window_minutes=5):self.auth_limit=auth_limit;self.spray_users=spray_users;self.volume_limit=volume_limit;self.window_minutes=window_minutes
 def evaluate(self,events:list[Event])->list[Alert]:
  alerts=[];by_ip=defaultdict(list)
  for event in events:by_ip[event.source_ip].append(event)
  for ip,values in by_ip.items():
   failures=[x for x in values if x.event_type is EventType.AUTH_FAILURE]
   group=next((g for g in _window_groups(failures,self.window_minutes) if len(g)>=self.auth_limit),None)
   if group:alerts.append(self._alert('AUTH_FAILURE_BURST','Repeated authentication failures',Severity.HIGH,ip,group,f'{len(group)} failed logins in {self.window_minutes} minutes'))
   spray=next((g for g in _window_groups(failures,self.window_minutes) if len({x.actor for x in g if x.actor})>=self.spray_users),None)
   if spray:alerts.append(self._alert('PASSWORD_SPRAY','Authentication failures across accounts',Severity.CRITICAL,ip,spray,f'{len({x.actor for x in spray if x.actor})} accounts targeted'))
   volume=next((g for g in _window_groups(values,self.window_minutes) if len(g)>=self.volume_limit),None)
   if volume:alerts.append(self._alert('EVENT_VOLUME_SPIKE','Abnormal event frequency',Severity.MEDIUM,ip,volume,f'{len(volume)} events in {self.window_minutes} minutes'))
  for event in events:
   if event.event_type is EventType.PRIVILEGE_CHANGE:alerts.append(self._alert('PRIVILEGE_CHANGE','Privilege or role changed',Severity.HIGH,event.source_ip,[event],f'{event.actor or "unknown actor"} changed {event.target or "a privilege"}'))
  unique={(x.rule_id,x.source_ip,x.window_start):x for x in alerts};return sorted(unique.values(),key=lambda x:(-list(Severity).index(x.severity),x.window_start,x.rule_id))
 def _alert(self,id,title,severity,ip,events,summary):return Alert(id,title,severity,ip,min(x.timestamp for x in events),max(x.timestamp for x in events),len(events),summary,tuple(x.event_id for x in events))
