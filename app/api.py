from fastapi import FastAPI
from .core import detect,stats
app=FastAPI(title="LogSentry")
events=[]
@app.post("/events")
def ingest(event:dict): events.append(event);return {"accepted":True}
@app.get("/alerts")
def alerts():return detect(events)
@app.get("/statistics")
def statistics():return stats(events)
