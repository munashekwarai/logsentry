from datetime import datetime,timezone
from app.core import detect,stats
def event(kind="auth_failure",ip="192.0.2.3"):return {"timestamp":datetime.now(timezone.utc).isoformat(),"event_type":kind,"source_ip":ip}
def test_repeated_failures(): assert detect([event() for _ in range(5)])[0]["severity"]=="HIGH"
def test_privilege_and_stats():
 e=[event("privilege_change")];assert detect(e)[0]["rule"]=="Privilege Change" and stats(e)=={"privilege_change":1}
