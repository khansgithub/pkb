## Personal Knowledge Base - WIP

Building a prototype knowledge base to consolidate small sippets of information I've kept in gists. 
The tool will primarily present a UI to search for differnet snippets based on their metadata.

Project is WIP and primarily for learning and experimentation.

## Technologies / Learning

- **Svelte**
- **Postgres**

## Progress

- **Parses markdown gist into a data structure, and merges in snipepts from comments**
- **Builds CSV row data (each row is a snippet)**
- **Stores data in Supabase, using full text search and trigram search for queries**
- **Exposes an API to query snippets**
  - `POST /search`
- **Front end search interface**

## Running

### Build CSV

```bash
cd parseGist
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
# imports `parseGist/parseGist/rows/blocks.csv + snippets.csv` into Supabase
```

### Run UI

```bash
cd front
npm i
npm run dev
```