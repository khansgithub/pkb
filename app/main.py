from functools import cache
from pathlib import Path

import uvicorn
from fastapi import Depends, FastAPI

from app.app_logging import logger
from app.embed import embed_text, embed_text_bert
from app.models import (ResponseHealth, ResponseSearch, ResponseSync,
                        SearchRequest)
from app.snippets import SnippetSource, SnippetSourceFile, SnippetSourceRaw
from app.vector import SklearnVectorStore, _SearchResults

snippet_source = SnippetSourceRaw()

app = FastAPI()


@cache
def get_store() -> SklearnVectorStore:
    return SklearnVectorStore()


@cache
def get_snipet_source() -> SnippetSource:
    # return SnippetSourceRaw()
    return SnippetSourceFile(Path(__file__).parent.absolute()/"gist.md")


@app.get("/health")
async def health():
    return ResponseHealth(status="OK")


@app.post("/sync")
async def sync(
    store: SklearnVectorStore = Depends(get_store),
    snippet_source: SnippetSource = Depends(get_snipet_source),
):
    # TODO: move logic out of here
    error = False
    try:
        snippets = await snippet_source.get_snippets()
        for snippet in snippets:
            logger.debug({"text being embedded", str(snippet)})
            # vec = embed_text(str(snippet))
            vec = embed_text_bert(str(snippet))
            store.add(vec, snippet)
        store.fit()
    except Exception as e:
        error = True
        logger.exception(e)
    return ResponseSync(
        success=not error,
        message=f"Sync {['complete','fail'][error]}",
        sync=None,
        meta={},
    )


@app.post("/search")
async def search(req: SearchRequest, store: SklearnVectorStore = Depends(get_store)):
    logger.debug({"search term": req.term})
    error = False
    results: _SearchResults = _SearchResults()
    try:
        vec = embed_text_bert(req.term)
        results = store.search(vec)
        logger.debug({"Results": results})
    except Exception as e:
        error = True
        logger.exception(e)
    return ResponseSearch(
        success=not error,
        message=f"Search {['complete','fail'][error]}",
        results=results.data,
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True,  reload_dirs=["app"])
