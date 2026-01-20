## pkb (Personal Knowledgebase) — PostgreSQL-first portfolio project

This repo started as an in-memory “local AI snippet search”. It’s now set up to become a **database-forward** project:

- **Ingest** markdown (`/sync`) into PostgreSQL (`documents`, `snippets`)
- **Search** with PostgreSQL **full-text search** (`tsvector` + **GIN index**) via `/search`
- Keep optional embedding code, but the core app runs without heavy ML dependencies

### What this demonstrates (DB skills)
- **Schema design**: `documents` ↔ `snippets` (FK + cascade)
- **Constraints**: unique document paths, idempotent snippet sync via content hashes
- **Indexes**: GIN on `tsvector`, plus supporting btree indexes
- **Generated columns**: stored `tsvector` for fast search
- **Migrations**: Alembic

### Setup (Windows)

Start Postgres:

```bash
cd pkb
docker compose up -d
```

Install backend deps:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Run migrations:

```bash
alembic upgrade head
```

Run the API:

```bash
python -m app.main
```

### API
- `GET /health`
- `POST /sync` (uses `PKB_SOURCE_PATH`, default `app/gist.md`)
- `POST /search` body: `{ "term": "git", "k": 5 }`

