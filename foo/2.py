import sys
from unittest.mock import MagicMock
import json 
from pathlib import Path

ollama_mock = MagicMock()
ollama_mock.OllamaLLM().invoke.return_value = ""

# import ipdb; ipdb.set_trace()
sys.modules["langchain_ollama"] = ollama_mock
sys.modules["langchain_huggingface"] = MagicMock()
from app import markdown
from app.snippets import ParseMardownAsSnippets

gist_path = Path(__file__).absolute().parent.parent / "app" / "gist_full.md"

lines = open(gist_path, "r", encoding="utf-8").read()

p = ParseMardownAsSnippets(lines)
data = p.parse_markdown()


with open(Path(__file__).parent / "data.json", "w", encoding="utf-8") as f:
    data_to_dump = [s.model_dump() for s in p._snippets]
    # data_to_dump = data
    json.dump(data_to_dump, f, ensure_ascii=False)

#b app/markdown.py:63