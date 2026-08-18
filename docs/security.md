# LogSentry Security

- Validate and redact at the producer: passwords, tokens, session IDs, payment data, and private payloads do not belong in security events.
- Event IDs are unique to prevent retry duplication; timestamps require timezone context; IP addresses are parsed; actor and metadata sizes are bounded.
- SQLite writes and filters are parameterized. API result limits and generator counts are bounded.
- Compose binds to loopback, runs non-root with a read-only root, and stores evidence separately.
- Real deployments require TLS, authenticated ingestion, authorization for search/alerts, tenant isolation, encryption, retention/deletion, rate limits, clock monitoring, and immutable evidence export.
- Generated fixtures are labelled `SIMULATED SECURITY EVENTS` and must not enter real incident evidence.
