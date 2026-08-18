from collections import Counter,defaultdict
from datetime import datetime,timedelta,timezone
ALLOWED={"auth_failure","auth_success","privilege_change","api_request"}
def normalize(x):
 missing={"timestamp","event_type","source_ip"}-x.keys()
 if missing:raise ValueError("missing fields: "+",".join(sorted(missing)))
 if x["event_type"] not in ALLOWED:raise ValueError("unsupported event type")
 dt=datetime.fromisoformat(x["timestamp"].replace("Z","+00:00"));return {**x,"timestamp":dt.astimezone(timezone.utc).isoformat()}
def detect(events,window_minutes=5,failure_limit=5,volume_limit=20):
 rows=[normalize(x) for x in events];alerts=[];by_ip=defaultdict(list)
 for x in rows:by_ip[x["source_ip"]].append(x)
 for ip,xs in by_ip.items():
  failures=[x for x in xs if x["event_type"]=="auth_failure"]
  for i,x in enumerate(failures):
   end=datetime.fromisoformat(x["timestamp"])+timedelta(minutes=window_minutes);n=sum(datetime.fromisoformat(y["timestamp"])<=end for y in failures[i:])
   if n>=failure_limit:alerts.append({"rule":"Repeated Authentication Failures","source":ip,"attempts":n,"window_minutes":window_minutes,"severity":"HIGH"});break
  if len(xs)>=volume_limit:alerts.append({"rule":"Abnormal Event Frequency","source":ip,"count":len(xs),"severity":"MEDIUM"})
 for x in rows:
  if x["event_type"]=="privilege_change":alerts.append({"rule":"Privilege Change","source":x["source_ip"],"severity":"HIGH"})
 return alerts
def stats(events):return dict(Counter(normalize(x)["event_type"] for x in events))
