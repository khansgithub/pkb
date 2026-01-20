import os
from dataclasses import dataclass, field
import re
from turtle import reset
from types import SimpleNamespace
from typing import List, Literal, Optional, TypedDict, cast
import ipdb
import json
import ipdb.stdout
from langchain_ollama import OllamaLLM
from langchain_core.messages import SystemMessage, HumanMessage, AIMessageChunk
from langchain_core.prompts import PromptTemplate
import logging

MODELS = ["codestral:latest", "mistral"]
llm = OllamaLLM(model=MODELS[0])


def get_data():
    data: list[list[str]] = []
    with open("comments_processed.json", "r") as f:
        data = json.load(f)
    return data


def parse_comments():
    data: list
    with open("comments.json", "r") as f:
        data = json.load(f)

    data = [
        list(map(lambda x: x.replace("\r", ""), d["body"].split("\n"))) for d in data
    ]

    with open("comments_processed.json", "w") as f:
        json.dump(data, f, indent=4)

    # ipdb.set_trace()


def extract_code_block_from_response(response: str) -> str:
    response = response[response.find("```") : response.rfind("```") + 1]
    llm_dataclass = response.replace("`", "")
    return llm_dataclass


def extract_code_block_from_response_stream(llm, messages):
    code_start = False
    code_start_i = 0
    code_stop_i = 0
    response = []
    x = 3
    for chunk in llm.stream(messages):
        # ipdb.set_trace()
        print(chunk, end="", flush=True)
        if not code_start:
            if code_start_i := chunk.find("`") >= 0:
                x -= chunk.count("`")
            else:
                if x < 2:
                    x = 3
            if x == 0:
                code_start = True
                print(">>CODE START>>")
                x = 3
                continue
        else:
            response.append(chunk)
            if code_stop_i := chunk.find("`") >= 0:
                x -= chunk.count("`")
            else:
                if x < 2:
                    x = 3
            if x == 0:
                print(">>CODE END>>")
                break

    response = "".join(response)
    print(response)
    print(response[code_start_i : code_stop_i + 1])


def print_llm_response_as_stream(llm: OllamaLLM, messages: list):
    chunks: list[str] = []
    for chunk in llm.stream(messages):
        chunks.append(chunk)
        print(chunk, end="", flush=True)


############################################################


def guess_schema():
    data = get_data()

    messages = [
        SystemMessage(
            content="Your job is to produce Python code. Repond with this template: Dataclass: <write the dataclass here> "
        ),
        HumanMessage(
            content=f"Take a look at this JSON data and build a single high-level Python dataclass that will fit each entry. JSON data: {json.dumps(data[0:6])} "
        ),
    ]

    llm_dataclass = extract_code_block_from_response(llm.invoke(messages))

    # print_llm_response_as_stream(llm, messages)
    i = 1
    while len(data) > 0:
        _data = json.dumps([data.pop() for _ in range(5) if len(data) > 0])
        messages = [
            SystemMessage(
                content='Responed to questions with a closed answer. Reply "Yes" or "No". If the response is "No", provide a suggestion with this template: Dataclass: <write the suggestion here>'
            ),
            HumanMessage(
                content=f"Take a look at this Python dataclass schema: {llm_dataclass}. Is this schema fit for this data? Data: {_data}. If not, please suggest a better high level schema for the data."
            ),
        ]
        llm_dataclass = extract_code_block_from_response(llm.invoke(messages))
        print(f"LLM Dataclass suggestion #{i}", llm_dataclass)
        i += 1

    # response = llm.invoke(messages)
    # print("LLM Dataclass suggestion #1", llm_dataclass)
    # print_llm_response_as_stream(llm, messages)


def build_serialiser_function():
    data: list[list[str]] = get_data()
    data_json = json.dumps(data[0:5])

#     schema = """
# @dataclass
# class SnippetResource:
#     language: str = 'Python'  # Assuming the code is always Python, if not, then make it str and provide the input data accordingly.
#     description: str = ''  # Description might be derived from the context or can be an empty string for now.
#     code_snippet: str  # Single string containing the entire block of Python code.
#     related_urls: Optional[List[str]] = field(default_factory=list)  # If multiple URLs are associated with the snippet
# """

#     messages = [
#         SystemMessage("Respond with the template: Function: <write the function here>"),
#         HumanMessage(
#             f"Analyse the JSON data, and the Python Dataclass. Write a function to serialise the data into the Dataclass object. \n JSON data: {data_json} \n Schema: {schema}"
#         ),
#     ]

#     print_llm_response_as_stream(llm, messages)

    llm_out = '''
            @dataclass
            class SnippetResource:
                language: str  # Assuming the code is always Python, if not, then make it str and provide the input data accordingly.
                description: str  # Description might be derived from the context or can be an empty string for now.
                code_snippet: str  # Single string containing the entire block of Python code.
                related_urls: Optional[List[str]] = field(default_factory=list)  # If multiple URLs are associated with the snippet


            def parse_json_to_dataclass(data):
                snippets = []
                for item in data:
                    if isinstance(item, list):
                        code = ''.join(item[0])
                        description = ''  # Assuming the description is not provided, modify as necessary.
                        snippet = SnippetResource('Python', description, code)
                        snippets.append(snippet)
                return snippets
    '''

    i = 1
    while len(data) > 0:
        _data = json.dumps([data.pop() for _ in range(10) if len(data) > 0])
        messages = [
            SystemMessage("Respond with the template: Function: <write the function here>"),
            HumanMessage(
                f"Analyse this code: {llm_out}. Assess how appropriate the function is to serialise this JSON data {_data} to included dataclass."
            ),
        ]
        # print(llm.stream(messages))
        print_llm_response_as_stream(llm, messages)
        input(" > ")


def serialise_data():
    data = get_data()
    schema = '''
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "SnippetResource",
  "type": "object",
  "properties": {
    "language": {
      "type": "string",
      "description": "Programming language of the snippet (e.g., Python)."
    },
    "description": {
      "type": "string",
      "description": "A human-readable description of the snippet."
    },
    "related_urls": {
      "type": "array",
      "description": "A list of related URLs associated with the snippet.",
      "items": {
        "type": "string",
        "format": "uri"
      },
      "default": []
    }
  },
  "required": ["language", "description"],
  "additionalProperties": false
}
'''
    r = []
    for d in data:
        messages = [
            SystemMessage('Respond in JSON using the template: {"output": {<your response here>}}'),
            HumanMessage(f"Using this JSON schema ({schema}), build a JSON representation for this markdown data: {d}")
        ]
        print(d)
        # print_llm_response_as_stream(llm, messages)
        response = llm.invoke(messages)
        print(response)
        # input(" > ")
    
    try:
        with open("serialised_data.json") as f:
            json.dump(r, f)
    except Exception as e:
        print(e)
        with open("serialised_data.json", "w") as f:
            f.writelines(r)


def serialise_data2():
    class CodeBlock(SimpleNamespace):
        lang: str
        code: list

    class FooOut(SimpleNamespace):
        block: CodeBlock
        other: list

    def foo(block: list[str]) -> FooOut:
        is_code = False
        code_block = CodeBlock(lang="", code=[])
        # code_block = {
        #     "lang": "",
        #     "code": []
        # }
        other = []
        for line in block:
            if not line: continue
            if not is_code:
                if line.strip().startswith("```"): is_code = True
                if len(lang:=line.split("```")) > 1:
                    lang = cast(str,lang[1]).strip()
                    code_block.lang = lang
                else:
                    # other
                    other.append(line.replace("- ", "", 1))
            elif is_code:
                if line.strip().startswith("```"): is_code = False
                else: code_block.code.append(line)
        # return [code_block, other]
        return FooOut(block=code_block, other=other)
    
    data = get_data()
    _data = []
    _lang = set()
    replacement0 = ["go", "pythong"]
    replacement1 = ["golang", "python"]
    replacements = {k: v for [k, v] in zip(replacement0,replacement1)}
    print(replacements)
    for i, d in enumerate(data):
        # if i == 4: ipdb.set_trace()
        b = foo(d)
        if b.block.lang == "" and b.other:
            b.block.lang = b.other[0]
        if b.block.lang in replacements:
            b.block.lang = replacements[b.block.lang]
        # if b.other and len(b.other[0].strip().split(" ")) == 1:
        #     if cast(str,b.other[0]).isalnum():
        #         b.other.pop(0)

        _lang.add(b.block.lang)
        _data.append(b)
        # os.system('cls')
        # for string in d:
        #     print(string)
        # input("")
        
    with open("serialised_data.json", "w") as f:
        json.dump(_data, f, indent=4, default=lambda x: x.__dict__)
    
    print(sorted(_lang))

# logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    serialise_data2()