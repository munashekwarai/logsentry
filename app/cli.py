import json,typer
from .core import detect
app=typer.Typer()
@app.command()
def analyze(path:str): print(json.dumps(detect([json.loads(x) for x in open(path) if x.strip()]),indent=2))
if __name__=="__main__":app()
