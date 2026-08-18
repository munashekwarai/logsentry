import json,typer
from .generator import SIMULATED_LABEL,generate
from .repository import Repository
from .service import LogSentry
app=typer.Typer(no_args_is_help=True)
def emit(x):print(json.dumps(x,indent=2,default=str))
@app.command()
def ingest(path:str,database:str='./data/logsentry.db'):
 service=LogSentry(Repository(database));count=0
 with open(path,encoding='utf8') as stream:
  for line in stream:
   if line.strip():service.ingest(json.loads(line));count+=1
 emit({'ingested':count})
@app.command()
def analyze(path:str,database:str=':memory:'):
 service=LogSentry(Repository(database))
 with open(path,encoding='utf8') as stream:
  for line in stream:
   if line.strip():service.ingest(json.loads(line))
 emit([x.to_dict() for x in service.alerts()])
@app.command()
def sample(output:str,seed:int=42,failures:int=8):
 with open(output,'w',encoding='utf8') as stream:
  for event in generate(seed=seed,failures=failures):stream.write(json.dumps(event)+'\n')
 emit({'label':SIMULATED_LABEL,'output':output,'events':failures+1})
@app.command()
def stats(database:str='./data/logsentry.db'):emit(Repository(database).stats())
if __name__=='__main__':app()
