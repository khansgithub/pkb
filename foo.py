import json
import logging
import re
from typing import Any, Callable, cast

import markdown
import numpy as np
from langchain_ollama import OllamaLLM
from sklearn.neighbors import NearestNeighbors


def debug():
    import ipdb

    ipdb.set_trace()


raw_text = """
# contents
- [git](#git)
- [s6](#s6)
- [docker](#docker)
- [python](#python)
- [go](#go)
- [linux](#linux)
- [tmux](#tmux)
- [redis](#redis)
- [curl](#curl)
- [nodejs](#nodejs)
- [typescript](#typescript)
- [stupid front end stuff](#stupidfrontendstuff)
- [vs code](#vscode)
- [k8](#k8)
- [kotlin](#kotlin)
---
# git
### global user.email user.name
```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```
#### switch user and choose which shell to use
```bash
su -s /bin/bash <user>
```
#### credential cache helper
```bash
git config --global credential.helper cache
git config --local credential.helper cache

git config --global --unset credential.helper
```
#### disable credential helper for single command
```bash
git clone https://bitbucket.org/<repo>.git --config credential.helper=
```

# s6
#### list services
```bash
ls /run/service/
```
#### restart service
```bash
s6-svc -r /run/service/svc-openssh-server
```

# docker
#### get docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```
#### list containers by name
```shell
docker ps -a --format "{{.Names}}" 
```
#### basic health check 
```shell
docker run \
    ...
    --health-cmd "set -e;  nc -zv localhost 22; if [ $? -eq 0 ]; then exit 0; else exit 1; fi" \
    --health-interval=10s 
    ...
```
### troubleshooting
#### Error response from daemon: client version 1.40 is too new...
```bash
# set to working version
DOCKER_API_VERSION=1.41
```
### etc
#### docker ps name and status format
```
docker ps --format "{{printf \"%-30s %-20s\" .Names .Status}}"
```
```
watch 'docker ps --format "{{printf \"%-30s %-20s\" .Names .Status}}"'
```

# python
#### monkeytype add type hints
```
# foo.py
import foo.bar
foo.bar.foobar()
```
```
monkeytype run foo.py
...
monkeytype apply foo.bar
```
#### interactive pdb
```python
import ipdb
ipdb.set_trace()
```
#### module structure
_https://ianhopkinson.org.uk/2022/02/understanding-setup-py-setup-cfg-and-pyproject-toml-in-python/_
```
├── README
├── pyproject.toml
├── setup.py
└── src
    └── foobar
        └── __init__.py
```
##### pyproject.toml
```
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```
##### setup.py
```python
#! /usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup()
```
#### install module develop mode
```bash
pip install --editable .
pip install -e .
```

# go
#### safe map look up
```golang
value, exists := foo["bar"]
if (!exists) {}
```
#### get go
```bash
# https://go.dev/doc/install
wget <tar_from_https://go.dev/doc/install>
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.20.3.linux-amd64.tar.gz
sudo ln -s /usr/local/go/bin/go /usr/bin/go
#sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.20.3.linux-amd64.tar.gz
```

# linux

#### jobs
```bash
# view jobs
jobs

# send job to background and stop
ctrl  + z

# resume background job
bg [job id]

# switch to job
fg [job id]

# run command as background job
tail -f log.txt &
```

#### cd follow sym link
```bash
cd -P ./sym-link-dir
```
#### list all listening ports and associated services
```bash
sudo netstat -tunlp
```
#### get umask
```bash
stat -c %a foo.txt
```

# tmux
#### basics
```
        new window - CTRL + b + c
     switch window - CTRL + b + [0-9]+
  vertical split | - CTRL + b + %
 horizonal split _ - CTRL + b + "
   navigate panels - CTRL + b + ↑ / ↓ / ← / →
```
### rename window / pane
#### window
```
CTRL + B + ,
```
#### pane
```
CTRL + B + :
select-pane -T <PANE NAME>
```
### session
#### minimise session
```
CTRL + b + d
```

#### attach to running session
```
tmux a
```
# redis
```
redis-cli
```
#### list keys
```
keys * 
```
#### read stream
```
xrange <key> - + 
```
#### find keys and pipe to delete
```
#             < query >
redis-cli keys rq:res* | awk '{print $1}' | xargs redis-cli del
```

# curl
#### pass file to curl as data
```
curl localhost:3000/workflow -X POST  -H 'Content-Type: application/json' --data-binary "@data.json"
```

# nodejs
#### set NODE_PATH
sometimes when using Node interactive, it might not be able to find global packages. hence it's necessary to set NODE_PATH
```
export NODE_PATH=$(npm root --quiet -g)
```
#### node_modules bin dir
```
/home/node/app/node_modules/.bin
```

# typescript
#### installing on corp VM
```
sudo apt-get update

sudo apt-get install -y ca-certificates curl gnupg
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
sudo chmod 644 /etc/apt/keyrings/nodesource.gpg

sudo apt-get update

sudo apt-get install nodejs -y

sudo npm install -g typescript
sudo chwon ubuntu -R /usr/lib/node_modules/typescript 
sudo chwon ubuntu /usr/lib/node_modules/typescript
```
#### debug in vscode
```typescript
// launch.json
{
    "type": "node",
    "request": "launch",
    "name": "ts debug",
    "skipFiles": ["<node_internals>/**"],
    "program": "${workspaceFolder}/src/index.ts",
    "runtimeArgs": ["-r", "ts-node/register", "-r", "tsconfig-paths/register"],
    "console": "internalConsole"
}

// tsconfig.json
{
    "sourceMap": true    
}
```
#### transpile multile ts files
```javascript
// /package.json
{
    "scripts": {
        "start": "nodemon ./src/index.ts"
    },
    "nodemonConfig": {
        "exec": "tsc && ts-node .",
        "ext": "ts"
    }
}

// /src/tsconfig.json
{
    ...
    "include": ["./src/frontend/foobar.ts"]
}

// /src/frontend/tsconfig.json
{
    "compilerOptions": {
        "module": "ES6",
        "target": "ES2017",
        "outFile": "./foobar.js",
        "rootDir": ".",
        "sourceMap": true,
        "noEmit": false
    }
}
```
# stupid front end stuff
#### appending innerHTML breaks all event listeners
```js
var html_to_insert = "<p>New paragraph</p>";

// with .innerHTML, destroys event listeners
document.getElementById('mydiv').innerHTML += html_to_insert;

// with .insertAdjacentHTML, preserves event listeners
document.getElementById('mydiv').insertAdjacentHTML('beforeend', html_to_insert);
```

# vs code
#### custom tasks
```json
// example file
// .vscode/tasks.json
{
	"version": "2.0.0",
	"inputs": [
		{
			"id": "imageName",
			"type": "promptString",
			"description": "Enter the image name",
			"default": "my-container-image"
		},
	],
	"tasks": [
		{
			"type": "typescript",
			"tsconfig": "portal/client/tsconfig.json",
			"problemMatcher": [
				"$tsc"
			],
			"group": "build",
			"label": "tsc: build - portal/client/tsconfig.json"
		},
		{
			"label": "Build Image",
			"type": "shell",
			"command": "podman",
			"args": [
				"build",
				"-f",
				"${file}",
				"-t",
				"${input:imageName}:${input:imageTag}"
			],
			"group": {
				"kind": "build"
			}
		}
	]
}
```
# k8
#### restart deployment
```bash
kubectl rollout restart deployment/core-service  -n osna 
```

# kotlin
#### kotlin vscode tasks
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Build Kotlin File with Kotlinc",
            "type": "shell",
            "command": "kotlinc ${file} -include-runtime -d ${fileBasenameNoExtension}.jar",
            "group": {
                "kind": "build",
                "isDefault":  "**/*.kt"
            },
            "problemMatcher": [],
            "windows": {
                "command": "kotlinc ${file} -include-runtime -d ${fileBasenameNoExtension}.jar"
            },
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Build Kotiln Gradle project",
            "type": "shell",
            "command": "IF EXIST gradlew.bat (gradlew build -x test) ELSE (echo 'gradlew.bat not found in the project root' && exit /b 1)",
            "options": {
                "cwd": "${workspaceFolder}"
            },
            "problemMatcher": [],
            "group": {
                "kind": "build",
                "isDefault": false
            }
        },
        {
            "label": "Run Kotiln Gradle project",
            "type": "shell",
            "command": "IF EXIST gradlew.bat (gradlew  run) ELSE (echo 'gradlew.bat not found in the project root' && exit /b 1)",
            "options": {
                "cwd": "${workspaceFolder}"
            },
            "problemMatcher": [],
            "group":{
                "kind": "run"
            }
        }
    ]
}
```
"""


def sklearn():
    def embed_fixed(text, size=10):
        # Convert text to ASCII numbers for letters only
        vec = np.array([ord(c) for c in text.lower() if c.isalpha()])
        # Truncate or pad to fixed size
        if len(vec) > size:
            vec = vec[:size]
        else:
            vec = np.pad(vec, (0, size - len(vec)))
        # Normalize (avoid division by zero)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    snippets = [
        "python ... first line of details second line of details', 'text being embedded",
    ]

    vectors = [embed_fixed(s) for s in snippets]

    nn = NearestNeighbors(metric="cosine")
    nn.fit(np.asarray(vectors))

    query = "python loop example"
    query_vec = embed_fixed(query)

    distances, indices = nn.kneighbors(
        np.asarray([query_vec]), n_neighbors=len(snippets)
    )

    print(f"Search results for '{query}':")
    for dist, idx in zip(distances[0], indices[0]):
        similarity = 1 - dist
        print(f"Similarity: {similarity:.3f} | Snippet: {snippets[idx]}")


def markdownit():

    md = markdown.Markdown(extensions=["toc"])

    md.convert(raw_text)
    import ipdb

    ipdb.set_trace()
    md_dict = getattr(md, "toc_tokens")
    md_json = json.dumps(md_dict)

    with open("temp.txt", "w") as f:
        f.writelines(md_json)


def m2j():
    import markdown_to_json

    raw_text = """
# git
## global
"""
    md_dict = markdown_to_json.dictify(raw_text)
    md_json = json.dumps(md_dict)

    with open("temp.json", "w") as f:
        f.writelines(md_json)


def custom_parse():
    #     raw_text = """
    # # git
    # ### global
    # """.splitlines()

    # heading / section parsing ################################################
    root: dict[str, list[Any]] = {}
    section_tracker = 0
    section = []
    current_section = []
    _last = "__last"
    new_section_index: Callable[[], dict[str | int, str | int]] = lambda: {_last: 0}
    section_index = new_section_index()
    line_is_heading = lambda line: line[0] == "#"
    line_is_codeblock = lambda line: line.startswith("```")
    new_section = lambda level, title: {"level": level + 2, "title": title}
    ############################################################################

    # code block parsing #######################################################
    is_code_block = False
    code_block_language = ""
    code_block = []
    guess_code_language = False
    llm = OllamaLLM(model="mistral")
    ###########################################################################

    def get_deepest_section(root: list, section_index, from_end=0):
        section = root
        _end_section: int = section_index[_last] - from_end
        for walk_dict in range(2, _end_section + 1):
            for section_entry in section:
                if isinstance(section_entry, dict):
                    sub_section_title = cast(str, section_index[walk_dict])
                    if sub_section_title in section_entry:
                        section = section_entry[sub_section_title]
                        break
        return section

    def get_root(section_index) -> list:
        return root[cast(str, section_index[1])]

    def _guess_codeblock_language(codeblock: list[str], path: str) -> str:
        code = r"\n".join(codeblock)
        template = (
            "I will give you a code block, and you will take a guess as to what language or DSL the code is in. "
            "Give me a single word answer, do not give me any further explanation at all."
            r"If you do not have 100% certainity of the language, reply with 'plaintext'."
            "I will also provide you with some text as context, to help you make a more accurate guess."
            "Use the context to take a educated guess."
            r"Respond in json, in the following format: {'prediction' : '<put your prediction here>'}"
            f"code block: \n\n{'\n'.join(code_block)}"
            f"context: {path}"
        )
        language_guess = llm.invoke(template)

        # language_guess = llm.invoke(f"Isolate the programming language or DSL in the follow text. " \
        #                             "If you cannot find one, return the first word in the given text. " \
        #                             r"Respond in json, in the following format: {'prediction' : '<put your prediction here>'} " \
        #                             f"Text: {language_guess}")
        # print("response: ", language_guess)
        lg_match = re.search("{(.*?)}", language_guess)
        if lg_match:
            # debug()
            lg_json: str = lg_match.group()
            try:
                lg_json = lg_json.replace("'", '"').lower()
                logging.debug("parsing: ", lg_json)
                lg_dict: dict[str, str] = json.loads(lg_json)
                language_guess: str | None = lg_dict.get("prediction")
            except (json.JSONDecodeError, TypeError):
                logging.error(f"Failed to guess codeblock language. {language_guess=}")
                language_guess = None

        logging.debug(f"{language_guess=}")
        return language_guess or ""

    def guess_codeblock_language(codeblock: list[str], path: str, n: int = 5) -> str:
        freq: dict[str, int] = {}
        max_freq_count = 0
        max_freq_word = ""
        for attempt in range(n):
            guess = _guess_codeblock_language(codeblock, path)
            if not guess:
                continue

            freq.setdefault(guess, 0)
            freq[guess] += 1
            count = freq[guess]

            if count > max_freq_count:
                max_freq_word = guess
        logging.debug(freq)
        return max_freq_word or ""

    #     ###
    #     raw_text = """
    # # one
    # ## two
    # #### four
    # #### four2
    # ### three
    # #### four3
    # ## two2
    # """
    #     ###
    for line in raw_text.splitlines():
        if not line:
            continue

        if line_is_codeblock(line):
            # start of code block
            if not is_code_block:
                is_code_block = True
                code_block_language: str = line[3:]
                if not code_block_language:
                    logging.error(
                        f"Section '{section_index[section_index[_last]]}' "
                        "is missing the Language for it's code block"
                    )
                    code_block_language = "plaintext"
                    guess_code_language = True
                    # raise Exception("Malformed code block")
                code_block = [code_block_language]

            # end of code block
            else:
                is_code_block = False
                if guess_code_language:
                    # grab all the headings and their values, except for the "_" headings which are empty headings
                    _headings_present = [
                        k
                        for k in section_index.keys()
                        if isinstance(k, int) and section_index[k] != "_"
                    ]

                    # get the title of all the headings and concat it
                    _path = ", ".join(
                        cast(list[str], [section_index[h] for h in _headings_present])
                    )

                    code_block_language = guess_codeblock_language(code_block, _path)

                code_block[0] = code_block_language or "plaintext"
                current_section.append(code_block)
                continue

        elif is_code_block:
            code_block.append(line)
            continue

        elif line_is_heading(line):
            heading_level = len(line.split(" ")[0])
            heading_title = line[heading_level + 1 :]

            if heading_level == 1:
                section_index = new_section_index()
                new_section = []
                root[heading_title] = new_section
                section_tracker = 1
                section_index[section_tracker] = heading_title

            elif heading_level > section_tracker:
                # start at the relative heading 1 section
                section = get_deepest_section(get_root(section_index), section_index)
                for x in range(section_tracker + 1, heading_level):
                    # missing subsections
                    new_section = []
                    section.append({"_": new_section})
                    section_index[x] = "_"
                    section_tracker = x
                    section = new_section

                current_section = []
                section.append({heading_title: current_section})

            elif heading_level < section_tracker:
                for x in range(heading_level, section_tracker + 1):
                    del section_index[x]
                # debug()
                section_index[_last] = heading_level - 1

                current_section = []
                section = get_deepest_section(
                    get_root(section_index), section_index
                ).append({heading_title: current_section})

            elif heading_level == section_tracker:
                current_section = []
                section = get_deepest_section(
                    get_root(section_index), section_index, from_end=1
                ).append({heading_title: current_section})

                section_index[heading_level] = heading_title

            section_index[heading_level] = heading_title
            section_index[_last] = heading_level
            section_tracker = heading_level
            # print(section_index)

        else:
            current_section.append(line)

    with open("temp.json", "w") as f:
        data = root
        f.writelines(json.dumps(data, indent=4))


# markdownit()
# m2j()
custom_parse()
