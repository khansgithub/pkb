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