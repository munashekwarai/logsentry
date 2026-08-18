"""LogSentry ingestion, search, statistics, and alert API."""
import os
from datetime import datetime
from fastapi import FastAPI,HTTPException,Query
from pydantic import BaseModel,Field
from .generator import SIMULATED_LABEL,generate
from .models import EventType
from .repository import DuplicateEventError,Repository
from .service import LogSentry
class EventInput(BaseModel):
 event_id:str=Field(min_length=1,max_length=128);timestamp:datetime;event_type:EventType;source_ip:str;actor:str|None=Field(None,max_length=254);target:str|None=Field(None,max_length=254);outcome:str|None=Field(None,max_length=50);metadata:dict=Field(default_factory=dict)
repository=Repository(os.getenv('LOGSENTRY_DB',':memory:'));service=LogSentry(repository);app=FastAPI(title='LogSentry',version='0.2.0')
@app.get('/health')
def health():return {'status':'ok','events':repository.stats()['total']}
@app.post('/events',status_code=201)
def ingest(value:EventInput):
 try:return service.ingest(value.model_dump()).to_dict()
 except DuplicateEventError as exc:raise HTTPException(409,str(exc)) from None
 except ValueError as exc:raise HTTPException(422,str(exc)) from None
@app.get('/events')
def search(start:datetime|None=None,end:datetime|None=None,event_type:EventType|None=None,source_ip:str|None=None,actor:str|None=None,limit:int=Query(100,ge=1,le=1000)):return [x.to_dict() for x in repository.search(start,end,event_type,source_ip,actor,limit)]
@app.get('/statistics')
def statistics(start:datetime|None=None,end:datetime|None=None):return repository.stats(start,end)
@app.get('/alerts')
def alerts(start:datetime|None=None,end:datetime|None=None):return [x.to_dict() for x in service.alerts(start,end)]
@app.post('/samples/generate')
def samples(seed:int=42,failures:int=Query(8,ge=1,le=100)):
 values=generate(seed=seed,failures=failures)
 for value in values:service.ingest(value)
 return {'label':SIMULATED_LABEL,'events':len(values)}
