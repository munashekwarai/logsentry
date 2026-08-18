# LogSentry Deployment

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e '.[dev]'
LOGSENTRY_DB=/var/lib/logsentry/logsentry.db uvicorn app.api:app --host 127.0.0.1 --port 8003
```

Or use `docker compose up --build -d`. Add an authenticating TLS proxy before remote access. Grant the service account write access only to the database directory. Define retention based on privacy and investigation requirements.

Use SQLite online backup or stop writers before copying. Encrypt backups and test search plus alert reconstruction after restore. For higher volumes, preserve normalized event IDs while moving to a streaming broker and scalable time-indexed store.
