# LogSentry Threat Model

| Threat | Implemented control | Deployment requirement |
|---|---|---|
| Log injection | Typed schema, JSON storage, no shell interpolation | Producer authentication and canonical signing if required |
| Duplicate/replayed events | Unique event ID | Producer idempotency and replay-window policy |
| Secret leakage in logs | Documentation and bounded metadata | Producer redaction/DLP and access reviews |
| Rule evasion by slow activity | Explicit five-minute assumption | Multiple windows, baselines, threat-informed tuning |
| False positives | Evidence IDs, counts, windows, explainable summaries | Human triage and feedback workflow |
| Database injection | Parameterized statements | Least-privilege filesystem and service account |
| Evidence deletion/tampering | Local history only | Append-only export, hashes/WORM retention, audit access logs |
| Resource exhaustion | Bounded payload fields, query/generator limits | Authenticated rate limits and scalable ingestion |
| Tenant data exposure | Single-instance reference has no tenants | Strong tenant partition and authorization before multi-tenancy |

LogSentry does not infer attacker identity, physical location, or intent. An alert proves a configured event pattern, not an attack. Completeness depends on producer coverage, timestamp accuracy, and retention.
