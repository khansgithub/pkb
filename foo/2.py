import sys
from unittest.mock import MagicMock
import json 
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

ollama_mock = MagicMock()
ollama_mock.OllamaLLM().invoke.return_value = ""

# import ipdb; ipdb.set_trace()
sys.modules["langchain_ollama"] = ollama_mock
sys.modules["langchain_huggingface"] = MagicMock()
from app import app_logging, markdown
from app.snippets import ParseMardownAsSnippets
logger = app_logging.logger.getChild(__name__)
gist_path = Path(__file__).absolute().parent.parent / "app" / "gist_full.md"

lines = open(gist_path, "r", encoding="utf-8").read()

markdown_to_snippets_parser = ParseMardownAsSnippets(lines)

#b app/markdown.py:63

def save_to_json_as_dict(markdown_to_snippets_parser: ParseMardownAsSnippets, filename: str) -> None:
    data = markdown_to_snippets_parser.parse_markdown()
    with open(Path(__file__).parent / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def save_to_json_as_snippets_array(markdown_to_snippets_parser: ParseMardownAsSnippets, filename: str) -> None:
    # As a side effect, the snippets are parsed and stored in parsed_to_snippets._snippets when `parse_markdown`` is called
    markdown_to_snippets_parser.parse_markdown()
    snippets_to_dump = [s.model_dump() for s in markdown_to_snippets_parser._snippets]
    # for snippet in snippets_to_dump:
    #     snippet["details"] = " ".join(snippet["details"])

    with open(Path(__file__).parent / filename, "w", encoding="utf-8") as f:
        # import ipdb; ipdb.set_trace()
        # data_to_dump = data
        logger.info(f"data length: {len(snippets_to_dump)}")
        json.dump(snippets_to_dump, f, ensure_ascii=False, indent=4)

def save_to_json_as_text_csv(markdown_to_snippets_parser: ParseMardownAsSnippets, filename: str) -> None:
    snippets_to_dump = [s.model_dump() for s in markdown_to_snippets_parser._snippets]
    with open(Path(__file__).parent / filename, "w", encoding="utf-8") as f:
        for snippet in snippets_to_dump:
            f.write(f"{snippet['language']},{snippet['title']},{" ".join(snippet['details'])}\n")

save_to_json_as_dict(markdown_to_snippets_parser, "data_dict.json")
save_to_json_as_snippets_array(markdown_to_snippets_parser, "data_snippets.json")
save_to_json_as_text_csv(markdown_to_snippets_parser, "data_snippets.csv")