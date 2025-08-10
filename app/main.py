from fastapi import FastAPI
import uvicorn

from models import HealthStatus
from snippets import SnippetRaw

snippet_source = SnippetRaw()

app = FastAPI()


@app.get("/health")
async def health():
    return HealthStatus(status="OK")

@app.post("/sync")
async def sync():
    snippets = await snippet_source.get_snippets()
    ... 

@app.post("/spotlight ")
async def spotlight ():
    ...


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
