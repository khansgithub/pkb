## Personal Knowledge Base - WIP

Building a prototype knowledge base to consolidate small sippets of information I've kept in gists. 
The tool will primarily present a UI to search for differnet snippets based on their metadata.
Aim is to use local AI to enrich the metadata for each snippet, and provide extra insights into the data and features.

Project is WIP and primarily for learning and experimentation.

## Technologies / Learning

- **Svelte**
- **Langchain**, **Ollama**, **SkLearn**
- **Postgres**

## Progress

- **Parses markdown gists into structured sections and snippets**
- **Models snippets as data**
- **Embeds snippets and performs similarity search (prototype)**
  - Embedding functions live in `app/embed.py` (currently includes CodeBERT-based embedding code)
  - Experiementing with differnt local models for best semantics
  - Also testing using Postgres for full-text search on metadata (without embedding the code itself), instead of using sklearn.
  - A lightweight in-memory vector store uses `sklearn.neighbors.NearestNeighbors` with cosine distance
- **Exposes a small FastAPI backend (prototype)**
  - `POST /sync` reads snippets and builds the vector index
  - `POST /search` embeds a query and returns nearest snippets
- **Front end search interface (prototype)**
  - Building a rich, heavy, interactive search interface.

## Running locally (WIP)

### Prereqs

- Python 3.11+ recommended
- Some embedding paths in `app/embed.py` require additional ML deps (e.g. `torch`, `transformers`). If you hit import errors, install the missing packages for your platform.

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run the API

```bash
python -m app.main
```

### Use the API

Build the in-memory index from `app/gist.md`:

```bash
curl -X POST http://localhost:8000/sync
```

Search:

```bash
curl -X POST http://localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"term":"docker healthcheck"}'
```

### UI

```bash
# /front/
npm run dev
```
