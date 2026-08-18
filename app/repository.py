"""SQLite normalized event storage, search, and statistics."""
import json,sqlite3
from datetime import datetime,timezone
from pathlib import Path
from .models import Event,EventType
class DuplicateEventError(ValueError):pass
class Repository:
 def __init__(self,path=':memory:'):
  if path!=':memory:':Path(path).parent.mkdir(parents=True,exist_ok=True)
  self.db=sqlite3.connect(path,check_same_thread=False);self.db.row_factory=sqlite3.Row
  self.db.executescript('''CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY,event_id TEXT UNIQUE NOT NULL,timestamp TEXT NOT NULL,event_type TEXT NOT NULL,source_ip TEXT NOT NULL,actor TEXT,target TEXT,outcome TEXT,metadata_json TEXT NOT NULL);
  CREATE INDEX IF NOT EXISTS events_time ON events(timestamp);CREATE INDEX IF NOT EXISTS events_source_time ON events(source_ip,timestamp);CREATE INDEX IF NOT EXISTS events_type_time ON events(event_type,timestamp);''')
 def add(self,event:Event):
  try:cur=self.db.execute('INSERT INTO events(event_id,timestamp,event_type,source_ip,actor,target,outcome,metadata_json) VALUES(?,?,?,?,?,?,?,?)',(event.event_id,event.timestamp.astimezone(timezone.utc).isoformat(),event.event_type.value,event.source_ip,event.actor,event.target,event.outcome,json.dumps(event.metadata,sort_keys=True)));self.db.commit();return self.get(cur.lastrowid)
  except sqlite3.IntegrityError:raise DuplicateEventError(f'event {event.event_id} already ingested') from None
 def get(self,id):
  x=self.db.execute('SELECT * FROM events WHERE id=?',(id,)).fetchone()
  if not x:raise KeyError(f'event {id} not found')
  return Event(id=x['id'],event_id=x['event_id'],timestamp=datetime.fromisoformat(x['timestamp']),event_type=EventType(x['event_type']),source_ip=x['source_ip'],actor=x['actor'],target=x['target'],outcome=x['outcome'],metadata=json.loads(x['metadata_json']))
 def search(self,start=None,end=None,event_type=None,source_ip=None,actor=None,limit=100):
  where=[];args=[]
  for clause,value in [('timestamp>=?',start.astimezone(timezone.utc).isoformat() if start else None),('timestamp<=?',end.astimezone(timezone.utc).isoformat() if end else None),('event_type=?',event_type.value if event_type else None),('source_ip=?',source_ip),('actor=?',actor)]:
   if value is not None:where.append(clause);args.append(value)
  sql='SELECT id FROM events'+(' WHERE '+' AND '.join(where) if where else '')+' ORDER BY timestamp DESC LIMIT ?';args.append(max(1,min(limit,1000)));return [self.get(x[0]) for x in self.db.execute(sql,args)]
 def stats(self,start=None,end=None):
  events=self.search(start,end,limit=1000);types={}
  for e in events:types[e.event_type.value]=types.get(e.event_type.value,0)+1
  return {'total':len(events),'by_type':types,'unique_sources':len({e.source_ip for e in events}),'window_start':start.isoformat() if start else None,'window_end':end.isoformat() if end else None}
