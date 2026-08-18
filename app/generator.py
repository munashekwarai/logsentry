"""Deterministic sample events; output is always labelled SIMULATED."""
import random,uuid
from datetime import datetime,timedelta,timezone
SIMULATED_LABEL='SIMULATED SECURITY EVENTS'
def generate(start=None,seed=42,failures=8):
 start=start or datetime.now(timezone.utc);rng=random.Random(seed);events=[]
 for i in range(failures):events.append({'event_id':str(uuid.UUID(int=rng.getrandbits(128))),'timestamp':(start+timedelta(seconds=i*20)).isoformat(),'event_type':'auth_failure','source_ip':'192.0.2.24','actor':f'user{i%5}@example.test','outcome':'denied','metadata':{'label':SIMULATED_LABEL}})
 events.append({'event_id':str(uuid.UUID(int=rng.getrandbits(128))),'timestamp':(start+timedelta(minutes=3)).isoformat(),'event_type':'privilege_change','source_ip':'198.51.100.8','actor':'admin@example.test','target':'role:manager','outcome':'success','metadata':{'label':SIMULATED_LABEL}});return events
