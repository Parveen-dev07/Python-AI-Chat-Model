# Database setup

## Customer database (development)

Configure a **read-only** PostgreSQL user when possible. For local development, set:

```env
CUSTOMER_DATABASE_URL=postgresql+psycopg://USER:PASSWORD@127.0.0.1:5433/DATABASE
DB_ALLOWED_SCHEMAS=public,auth
DB_QUERY_TIMEOUT_SECONDS=10
DB_MAX_ROWS=100
```

Use the `postgresql+psycopg://` driver prefix for SQLAlchemy 2 + psycopg3.

## Sample menu table (optional)

```sql
CREATE TABLE IF NOT EXISTS public.menu_items (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  price NUMERIC(10, 2) NOT NULL
);

INSERT INTO public.menu_items (name, price)
VALUES ('Demo Burger', 199.00)
ON CONFLICT DO NOTHING;
```

Grant SELECT to your read-only role on allowed schemas only.

## Health check

`GET /health/database` runs `SELECT 1` using `CUSTOMER_DATABASE_URL`. Failures return a generic message; details are logged server-side.

## Platform configuration database

Not required for the first prototype. Tenant and widget metadata are loaded from environment variables via `TenantResolver`. A dedicated platform DB may be added later with Alembic migrations.
