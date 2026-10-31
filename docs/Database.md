# Database (portable stubs)

## Is PostgreSQL right for “most” Python projects?

| Use case | Good default | Why |
|----------|--------------|-----|
| Multi-user app, migrations, integrity, concurrent writers | **PostgreSQL** | Mature, free, excellent tooling, strong SQL |
| Local single-user tool, simple storage | **SQLite** | Zero server, one file |
| Heavy **time-series** (metrics, events, retention windows) | **Postgres + TimescaleDB** (or similar) | Hypertables, compression, time-oriented queries |
| Huge analytics warehouse | Often **not** OLTP Postgres alone | Consider warehouse tools later |

**Generic rule:** start with **Postgres** if you need a real server DB; start with **SQLite** if you need “no install.” Add Timescale (or another time-series extension) only when the workload justifies it.

---

## Intake (agent asks)

- [ ] DB? none / SQLite / PostgreSQL / Postgres+Timescale / other  
- [ ] Local only or remote host?  
- [ ] Need backups? Y / N  
- [ ] Need migrations/versioned schema? Y / N  

---

## PostgreSQL — install & wire

**Installers:** [postgresql.org/download](https://www.postgresql.org/download/) — [Windows](https://www.postgresql.org/download/windows/) · [macOS](https://www.postgresql.org/download/macosx/) · [Linux](https://www.postgresql.org/download/linux/)

1. Install Postgres. Note port (default **5432**) and superuser password; store the password outside git.
2. Create a role + database for the app (not superuser for daily use).
3. App `.env` (never commit):

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=your_app
POSTGRES_USER=your_app
POSTGRES_PASSWORD=...
# or DATABASE_URL=postgresql://user:pass@localhost:5432/your_app
```

4. Python: `pip install psycopg[binary]` (or poetry/uv equivalent).
5. Schema: keep SQL under `db/` or `src/.../sql/` with a version note; apply via script or migration tool.
6. **Query text:** multi-line SELECT/INSERT/upsert/report SQL also lives in those `.sql` files (load by name). Do not bury full statements as string literals in stores or UI — see Coding_Standards § SQL lives in files.
7. Backup: `pg_dump` on a schedule and before destructive migrations.

### Optional TimescaleDB

- Install the Timescale extension into the same Postgres instance when intake says time-series heavy.
- Use hypertables on time + entity keys only if retention/volume warrants it.

---

## SQLite stub

- File path in config (e.g. `data/app.db`).
- stdlib `sqlite3` or SQLAlchemy.
- Fine for single writer; careful with concurrent UI + workers.

---

## Other DBs

| Engine | When to consider |
|--------|------------------|
| MySQL / MariaDB | Existing shop standard |
| SQL Server | Windows enterprise shops |
| MongoDB | Document-shaped data (not a free “no schema” pass) |

Add a short `docs/Database_<Engine>.md` only when chosen — keep this file as the decision tree.

---

## Schema / UI inventory (optional later)

- Versioned DDL + Change_Log when schema changes.
- Optional admin UI listing tables/row counts (app-specific). If you build one, name it for **inventory / data report**, not ambiguous “health,” unless medical is the product domain.
