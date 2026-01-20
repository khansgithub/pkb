import os
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.app_logging import logger
from app.db import get_db
from app.db_models import Document, Snippet
from app.ingest import extract_snippets_from_markdown, load_markdown_file
from app.schemas import (
    ResponseHealth,
    ResponseSearch,
    ResponseSync,
    ResponseSyncBody,
    SearchRequest,
    SearchResult,
    SnippetOut,
)

app = FastAPI(title="pkb", version="0.2.0")


@app.get("/health")
async def health():
    return ResponseHealth(status="OK")


@app.post("/sync")
async def sync(db: Session = Depends(get_db)):
    """
    Ingest a markdown file into PostgreSQL.
    Default source is controlled by PKB_SOURCE_PATH (defaults to app/gist.md).
    """
    source_path = Path(os.getenv("PKB_SOURCE_PATH", "app/gist.md"))
    if not source_path.exists():
        raise HTTPException(status_code=400, detail=f"Missing source file: {source_path}")

    raw, sha = load_markdown_file(source_path)
    extracted = extract_snippets_from_markdown(raw)

    try:
        with db.begin():
            doc = db.query(Document).filter(Document.path == str(source_path)).one_or_none()
            if doc is None:
                doc = Document(path=str(source_path), sha256=sha)
                db.add(doc)
                db.flush()  # ensure doc.id
            else:
                doc.sha256 = sha

            # Idempotent re-sync: replace snippets for this document
            db.query(Snippet).filter(Snippet.document_id == doc.id).delete()

            rows = [
                Snippet(
                    document_id=doc.id,
                    snippet_hash=s.snippet_hash,
                    title=s.title,
                    heading_path=s.heading_path,
                    language=s.language,
                    code=s.code,
                )
                for s in extracted
                if s.code.strip()
            ]
            db.add_all(rows)

        return ResponseSync(
            success=True,
            message="Sync complete",
            sync=ResponseSyncBody(
                document_path=str(source_path),
                document_sha256=sha,
                snippets_loaded=len(extracted),
                snippets_written=len(rows),
            ),
            meta={},
        )
    except Exception as e:
        logger.exception(e)
        return ResponseSync(
            success=False,
            message="Sync failed",
            sync=None,
            meta={"error": str(e)},
        )


@app.post("/search")
async def search(req: SearchRequest, db: Session = Depends(get_db)):
    """
    PostgreSQL full-text search over snippets (FTS + GIN index).
    """
    q = req.term.strip()
    k = max(1, min(req.k, 50))

    sql = text(
        """
        WITH query AS (
          SELECT plainto_tsquery('english', :q) AS tsq
        )
        SELECT
          s.id,
          s.title,
          s.heading_path,
          s.language,
          s.code,
          d.path AS document_path,
          ts_rank_cd(s.tsv, query.tsq) AS score
        FROM snippets s
        JOIN documents d ON d.id = s.document_id
        JOIN query ON TRUE
        WHERE s.tsv @@ query.tsq
        ORDER BY score DESC, s.id DESC
        LIMIT :k
        """
    )

    rows = db.execute(sql, {"q": q, "k": k}).mappings().all()
    results = [
        SearchResult(
            score=float(r["score"]),
            snippet=SnippetOut(
                id=int(r["id"]),
                title=r["title"],
                heading_path=r["heading_path"],
                language=r["language"],
                code=r["code"],
                document_path=r["document_path"],
            ),
        )
        for r in rows
    ]

    return ResponseSearch(success=True, message="Search complete", results=results)


@app.post("/query")
async def query_alias(req: SearchRequest, db: Session = Depends(get_db)):
    """
    Backwards-compatible alias for older front-end clients.
    """
    return await search(req=req, db=db)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
    )
