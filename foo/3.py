from langchain_ollama import OllamaLLM
from langchain_core.messages import HumanMessage
from pathlib import Path
import json 

doc = ""
comments = []
llm = OllamaLLM(model="codestral:latest")

with open(Path(__file__).parent.parent / "comments.json") as f:
    comments = json.load(f)

with open(Path(__file__).parent.parent / "app" / "gist.md") as f:
    # doc = json.load(f)
    doc = f.readlines()

conversation = [
    HumanMessage(f"Looking at this markdown data ```{doc}```, pick a section to place this snippet ```{comments[1]["body"]}```.")
]

def print_llm_response_as_stream(llm: OllamaLLM, messages: list):
    chunks: list[str] = []
    for chunk in llm.stream(messages):
        chunks.append(chunk)
        print(chunk, end="", flush=True)

response = print_llm_response_as_stream(llm, conversation)