# Security

## Current prototype controls

- Tenant/database URLs resolved **server-side** only (`TenantResolver`).
- SQL validated for **single SELECT** statements; dangerous keywords rejected.
- Schema allowlist via `DB_ALLOWED_SCHEMAS`.
- Query timeouts and row limits on execution.
- `X-API-Key` required for chat and widget config endpoints.
- Basic per-IP rate limiting on chat.
- Generic error messages to clients; no SQL or connection string leakage in responses.

## Not production-ready yet

Before public deployment, plan for:

- Stronger authentication (signed widget tokens, mTLS, or OAuth between services).
- Domain allowlists enforced server-side per widget.
- Dedicated read-only DB users with column/table grants.
- Audit logging and secret rotation.
- WAF / reverse proxy rate limits and TLS termination.
- Penetration testing and dependency scanning.

## Widget and API keys

Exposing `X-API-Key` in browser bundles is convenient for demos but **unsafe for production**. Use a backend proxy so secrets never ship to end users.
