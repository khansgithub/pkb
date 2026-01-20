# contents
- [android](#android)
- [bash](#bash)
- [css](#css)
- [curl](#curl)
- [docker](#docker)
- [git](#git)
- [go](#go)
- [k8](#k8)
- [kotlin](#kotlin)
- [linux](#linux)
- [misc](#misc)
- [nodejs](#nodejs)
- [python](#python)
- [redis](#redis)
- [rust](#rust)
- [s6](#s6)
- [sql](#sql)
- [stupid front end stuff](#stupidfrontendstuff)
- [svelte](#svelte)
- [tmux](#tmux)
- [typescript](#typescript)
- [vs code](#vscode)
- [vue](#vue)
- [web](#web)

# git

## global user.email user.name

```bash
git config --global user.email "you@example.com"
git config --global user.name "Your Name"
```

## credential cache helper
```bash
git config --global credential.helper cache
git config --local credential.helper cache

git config --global --unset credential.helper
```

## disable credential helper for single command
```bash
git clone https://bitbucket.org/<repo>.git --config credential.helper=
```

# cue 
## output cue file to json
```bash
cue eval schema.cue --out json
```

# s6

## list services
```bash
ls /run/service/
```

## restart service
```bash
s6-svc -r /run/service/svc-openssh-server
```

# docker
## docker build creates cache, which can add up
```bash
docker builder prune
```

## get docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker
```

## list containers by name
```shell
docker ps -a --format "{{.Names}}" 
```

## basic health check 
```shell
docker run \
    ...
    --health-cmd "set -e;  nc -zv localhost 22; if [ $? -eq 0 ]; then exit 0; else exit 1; fi" \
    --health-interval=10s 
    ...
```

## troubleshooting

### Error response from daemon: client version 1.40 is too new...
```bash
# set to working version
DOCKER_API_VERSION=1.41
```

## etc

### docker ps name and status format
```bash
docker ps --format "{{printf \"%-30s %-20s\" .Names .Status}}"
```
```bash
watch 'docker ps --format "{{printf \"%-30s %-20s\" .Names .Status}}"'
```

# python

## etc

### 1px loading icon with the cursor set to the start of the line. this makes it so when another thread prints to stdout, it will overwrite the loading logo.
```python
def loading_dots2(end_event: Event, sleep_duration: float = 1 / 4):
    animation = cycle(["|", "/", "-", "\\"])
    hide_cursor = "\033[?25l"
    show_cursor = "\033[?25h"
    clear_line = "\r\033[K"
    cursor_to_start_of_line = "\r"

    sys.stdout.write(hide_cursor)
    sys.stdout.flush()
    try:
        while not end_event.is_set():
            sys.stdout.write(hide_cursor)
            sys.stdout.write(clear_line)
            sys.stdout.write(next(animation))
            sys.stdout.write(cursor_to_start_of_line)
            sys.stdout.flush()
            time.sleep(sleep_duration)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(clear_line)
        # sys.stdout.write(show_cursor)
        sys.stdout.flush()
```


### protocol vs abc
### https://medium.com/@pouyahallaj/introduction-1616b3a4a637


### to force typecast use `cast`
```python
from typing import cast
a: str | None = "foo"
b: str = cast(str, a)
```

### use seconds if it's >60 or minutes, and add 's' . uses the fact that `string="a"[:-1]` gives the empty string
```python
f"{[f'{(s:=sleep_duration)} second', f'{(m:=sleep_duration//60)} minute'][s>=60] + 's'[:m>1 or (s> 1 and m < 1)]}"
```


### all try/catch blocks of code, should have a unit test associated with it


### forward declare 
```python
def foo() -> "SomeClass":
    ...
```


### add a function to an object instance and have it take self
```python
mock_workflow_mocker.proxy_configure_mock = types.MethodType(proxy_configure_mock, mock_workflow_mocker)
```


### typing a function that returns `self`
```python
from typing import Self
def foo(self) -> Self:
    return self
```


### learnings for making programs easier to test
1. ***never*** define top level variables, which at any point require connectivity (ssh, http, etc...). keep them dumb.
2. try consolidate all networking functionality into a class which deals with its lifecycle. make a getter that returns connection objects
```python
def get_netbox() -> api:
  global nb
  return nb if nb else setup_nb()
```

### function which might be passed an RLock or None
```python
with stdout_lock or nullcontext():
    logger.info(f"Polled {hostname} successfully")
```


### when extending multiple classes, the functions of the first class takes precedence
``` python
class A:
    def __init__(self):
        print("A.__init__")

class B:
    def __init__(self):
        print("B.__init__")

class AB(A, B): ...
    
ab = AB()
# > A.__init__
```


### go through all child mocks created (properties of mocks)
``` python
    children_list = [
        *list(mock_netbox._mock_children.items())
    ]
    all_children_mocks = []
    # import ipdb; ipdb.set_trace()
    while children_list:
        children = children_list.pop()
        print(children)
        all_children_mocks.append(children)
        if (c:=list(children)[1]._mock_children.items()):
            for child in c:
                children_list.append(list(child))
```



### monkeytype add type hints
```python
# foo.py
import foo.bar
foo.bar.foobar()
```
```bash
monkeytype run foo.py
...
monkeytype apply foo.bar
```

### interactive pdb
```python
import ipdb
ipdb.set_trace()
```


### mock all missing imports dynamically
```python
import sys
from unittest.mock import MagicMock

mod = None
missing_mod = False

while missing_mod:
    if mod:
        print("Adding: " + mod)
        sys.modules[mod] = MagicMock()
        mod = False
    try:
        # import lines go here
    except ModuleNotFoundError as e:
        mod = e.msg.split(" ")[3].translate(str.maketrans('','','";\''))
        print("Missing: " + mod)
        missing_mod = True
        # input("> ")
# sys.exit(0)
# resume rest of the code
```

### asyncio
```python
if __name__ == "__main__":
    clean_up_loop = False
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run())
    except Exception:
        clean_up_loop = True
        pass
    finally:
        async def close_sessions_and_consumers():
            for k in kafka.CONSUMERS:
                await k.stop()
            await kafka.SESSION.close()
        loop.run_until_complete(close_sessions_and_consumers())

        if clean_up_loop:
            pending = asyncio.all_tasks()
            for task in pending:
                task.cancel()
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
            loop.stop()
            loop.close()
```

### shared class field across all object instances
```python
from typing import List

class Foo()
    static_field: List[int] = []

    def __init__(self, i: int):
        self.static_field.append(i)
    
    def getList(self) -> List[int]:
        return self.static_field

a = Foo(1)
b = Foo(999)

print (a.getList())
print (b.getList())

'''
[1, 999]
[1, 999]
'''
```


### `__post_init__` for dataclasses
- https://testdriven.io/tips/94ca0d2c-4c0d-4b8f-9762-6daa11d504f7/


### function overload
- `functools.singledispatch` only dispatches on the type of the first argument.
```python
from functools import singledispatch

@singledispatch
def func(arg):
    print(f"Default: {arg}")

@func.register(int)
def _(arg):
    print(f"Integer: {arg}")

@func.register(str)
def _(arg):
    print(f"String: {arg}")

func(1)        # Output: Integer: 1
func('hello')  # Output: String: hello
```


### `str.startswith` and `str.endswith` can take a `Tuple` as a parameter (https://docs.python.org/3/library/stdtypes.html#str.startswith)
```python
interface["name"].startswith(("ge", "xe", "ae", "et"))
```


### decorators are applied from **bottom up**
```python
def b():
    print("Running function: b")

def a():
    print("Running function: a")

def main():
    return_a = a()
    return_b = b()
    
    print(f"{return_a=}, {return_b=}")

@patch("__main__.b")  # <- Second parameter to `mock`
@patch("__main__.a")  # <- First parameter to `mock`
def mock(a: MagicMock, b: MagicMock,):
    a.return_value = "mocked a"
    b.return_value = "mocked b"
    main()
    
mock()
'''
 > return_a='mocked a', return_b='mocked b'
'''
################

@patch("__main__.a")
@patch("__main__.b")  # <- First parameter, mismatched with naming it parameter 'a;MagicMock'
def mock(a: MagicMock, b: MagicMock,):
    a.return_value = "mocked a"
    b.return_value = "mocked b"
    main()
'''
> return_a='mocked b', return_b='mocked a'
         ^         ^ 
    mocked with wrong value
'''
```


### disable default console logger after adding more handlers by disabling `propagate`
```python
logger = logging.getLogger("foo")
rh = RichHandler(show_level=True, show_path=True,
                        markup=True, rich_tracebacks=True)

logger.handlers = [rh]
logger.propagate = False
```


### preserve type inference of wrapped functions (i don't get how this works, need to read it later, but it works)
- https://stackoverflow.com/a/74080156


## poetry
### usage
```bash
poetry new <project name>
cd <project name>
poetry lock
poetry add [list of packages to add]
poetry add --editable <path to editable another python repo>
poetry install # this actually installs the packages into site_packages in a new venv

poetry shell # activate python venv
python3 main.py
exit
```

### poetry make venv locally
``` bash
# poetry.toml
[virtualenvs]
in-project = true

# OR

# locally
poetry config virtualenvs.in-project true --local

# OR 

# globally
poetry config virtualenvs.in-project true
```

## pytest
### label a test, and run all tests with that label
```python
# test.py
@pytest.mark.solo
def test_solo(mocker):
    pass
```
```
# pytest.ini
[pytest]
markers =
    solo: mark a test as a solo test
```

```bash
pytest -m solo
```

### run a specific `pytest` (with stdout collection)
```bash
pytest -s ./tests/test_exception_handlers.py::test_exception_handler
```


## mypy
### mypy to text with certain logs removed
```bash
mypy foo.py > mypy.txt; sed -i -e note:/d' -e '/of "Logger"/d' -e '/\[import-untyped\]/d' mypy.txt; less mypy.txt 
```

## error handling
### log an exception with traceback

```python
import logging

fooLogger = logging.getLogget("foo")

def foo():
    try:
        raise Exception("foo error")
    except Exception as e:
        fooLogger.exception(e)
```

### catch multiple class of exceptions in one block
```python
try:
    foo()
except (Exception, KeyboardInterrupt) as e:
    if isinstance(e, KeyboardInterrupt):
        print('KeyboardInterrupt')
    else:
        pass
```


### decorator
- error handling in decorators can be difficult. is there is a try block inside the decorator, and the calling function was passed with incorrect parameters, the traceback only show the try block inside the decorator. the calling function, which called the decorated function with wrong parameters, will not be shown.
## the takeaway might be to always raise exceptions in a decorator 
```python
1	import logging
2	from abc import ABC
3	import functools
4	from typing import Callable, TypeVar, ParamSpec, Any
5	P = ParamSpec("P")
6	T = TypeVar("T")
7	logging.basicConfig(level=logging.DEBUG)
8	def calling_function():
9	    decorator(a=2) # decorator will call `foo`` with wrong parameters, but the main invoker is this function
10	    
11	def decorator(*args, **kwargs):
12	    try:
13	        foo(*args, **kwargs)
14	    except Exception:
15	        # the traceback will be printed here, but it will not show that `calling_function` passed the values to `decorator`
16	        logging.exception("An error occurred")
17	def foo():
18	    pass
19	calling_function()
```

### async
- correct way to error handle an **async** Task, scheduled with `asyncio.create_task`. don't use `asyncio.add_done_callback(cb)` because it will not  properly capture the traceback when getting the error with `def cb(task): ... task.exception()`(for some reason idk)
```python
t: Task = asyncio.create_task(foo())

# for async tasks only because non-async tasks just crash the whole event loop
async def foo():
  # use try/except here to error handle
  try:
    function_that_errors()
  except Exception as e:
    logging.exception(e)
```

## pyenv

### some libraries required
```bash
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git libgdbm-dev libnss3-dev
pyenv install 3.11
```

### set global python version 
```bash
> pyenv versions
  system
* 3.11.9 (set by /root/.pyenv/version)
> pyenv global 3.11.9
```


### script to install `pyenv` to install `python` to install `pipx` to install `poetry` ...
```bash
apt-get install locales
localedef -i en_US -f UTF-8 en_US.UTF-8

apt install curl

curl https://pyenv.run | 

for file in .bash_profile .profile .bashrc; do
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/$file
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/$file
    echo 'eval "$(pyenv init -)"' >> ~/$file
done

echo 'eval "$(pyenv virtualenv-init -)"' >> ~/.bashrc

apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git libgdbm-dev libnss3-dev
pyenv install 3.11

# restart shell
bash

pyenv global 3.11.9

python -m pip install --user pipx

python -m pipx ensurepath

python -m pipx completions

eval "$(register-python-argcomplete pipx)"

# restart shell
bash

pipx install poetry
```

## django
### server event stream in django
```python
async def SSEStream(request: HttpRequest):
    async def stream():
        _cached_count = None
        while True:
            _cached_count = count
            yield (
                'event: event name'
                '\n'
                f'data: data'
                '\n\n' # <- must be 2 new lines to end a message
            )
        await sleep(1.0)
    return StreamingHttpResponse(stream(), content_type='text/event-stream')

# usage: urls.py
urlpatterns =  [path('stream', SSEStream, name='stream')]
```


### django interactive shell
```python
# channels example
$ python3 manage.py shell
import channels.layers
channel_layer = channels.layers.get_channel_layer()
from asgiref.sync import async_to_sync
async_to_sync(channel_layer.send)('test_channel', {'type': 'hello'})
async_to_sync(channel_layer.receive)('test_channel')
{'type': 'hello'}
```


## lint + formatting
```bash
poetry add -D black ruff pylint isort
set FILE=config.py && isort %FILE%  && black %FILE% && ruff check %FILE% --fix  && mypy %FILE%
```

## rich logger
```python
import logging

from rich.logging import RichHandler

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("app")
logger.handlers = [RichHandler(rich_tracebacks=True)]
logger.level = logging.DEBUG
logger.propagate = False
```

## module structure
- https://ianhopkinson.org.uk/2022/02/understanding-setup-py-setup-cfg-and-pyproject-toml-in-python/
```
├── README
├── pyproject.toml
├── setup.py
└── src
    └── foobar
        └── __init__.py
```

### pyproject.toml
```
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"
```

### setup.py
```python
#! /usr/bin/env python

from setuptools import setup

if __name__ == "__main__":
    setup()
```

### install module develop mode
```bash
pip install --editable .
pip install -e .
```

# go

## bypass unused function error

``` golang
(func(args... interface{}){})(scrape_cpu, scrape_hostname)
```

```golang
go fmt ./...
```

## embedded types
```go
type Person struct {
  Name string
}
func (p *Person) Talk() {
  fmt.Println("Hi, my name is", p.Name)
}

type Android struct {
  Person // Android is also type Person!
  Model string
}

a := new(Android)
a.Person.Talk()

a.Talk() // polymorphism!
```

## mutex classes
  - sync.RWLock()
  - sync.Once

## init function in packages
```go
var Foo string
// runs like package constructor
func init(){
    Foo = "foobar"
}
```

## type signature for parameters of self containing recursive functions
```go
func getLastLetterRecursivley(word string) {
    type rFunc func(string, rFunc) // <- allows recursive function to be defined
    var f rFunc = func(word string, f rFunc) {
        if len(word) == 1 {
            fmt.Println("Last character is:", word)
            return
        }
        f(word[len(word) - 1: ], f)
        return
    }
    go f(x, f)
    for {} // keep function running to we can still print
}
```

## generics + type constraint
```go
type StringOrInt interface{
	string | int
}

func main() {
	{
		var x = foo[int]()
		fmt.Println(x)
	}

	{
		var x = foo[string]()
		fmt.Println(x)
	}

	{
		var x = foo[bool]() // err
		fmt.Println(x)
	}

}

func foo[T StringOrInt]() []T {
	var x T
	return []T{x}
}
```

## `struct`s cannot be `const` because they're inherently composite types

## safe map look up
```golang
value, exists := foo["bar"]
if (!exists) {}
```

## get go
```bash
# https://go.dev/doc/install
wget <tar_from_https://go.dev/doc/install>
rm -rf /usr/local/go && tar -C /usr/local -xzf go1.20.3.linux-amd64.tar.gz
sudo ln -s /usr/local/go/bin/go /usr/bin/go
#sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.20.3.linux-amd64.tar.gz
```

# linux

## tar switches
```
https://superuser.com/a/156215
x - extract files
c - create archive
t - list files
v - verbose (list files as it processes them)
j - use bz2 compression
z - use gz compression
f - read or write files to disk
Examples

Uncompress a tar.gz file: tar zxf tarball.tar.gz

Uncompress a tar.bz2 file: tar jxf tarball.tar.bz2

Create a tar.gz file: tar zcvf tarvall.tar.gz mydir/*
```

## kill a proc in `jobs` using `%` syntax
```bash
jobs
> [1]+  Running                 poetry run main &
kill -9 %1
> [1]+  Killed                  poetry run main
```

## jobs
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

## cd follow sym link
```bash
cd -P ./sym-link-dir
```

## list all listening ports and associated services
```bash
sudo netstat -tunlp
```

## get umask
```bash
stat -c %a foo.txt
```

# tmux

## basics
```
        new window - CTRL + b + c
     switch window - CTRL + b + [0-9]+
  vertical split | - CTRL + b + %
 horizonal split _ - CTRL + b + "
   navigate panels - CTRL + b + ↑ / ↓ / ← / →
```

## rename window / pane

### window
```
CTRL + B + ,
```

### pane
```
CTRL + B + :
select-pane -T <PANE NAME>
```

## session

### minimise session
```
CTRL + b + d
```

### attach to running session
```bash
tmux a
```

# redis
```bash
redis-cli
```

## list keys
```bash
keys * 
```

## read stream
```bash
xrange <key> - + 
```

## find keys and pipe to delete
```bash
#             < query >
redis-cli keys rq:res* | awk '{print $1}' | xargs redis-cli del
```

# curl

## pass file to curl as data
```bash
curl localhost:3000/workflow -X POST  -H 'Content-Type: application/json' --data-binary "@data.json"
```

# nodejs

- `fs.readdir` is NOT blocking; use `fs.readdirSync` instead

## run node tools from cli
```
npx tsc
```

## set NODE_PATH
- sometimes when using Node interactive, it might not be able to find global packages. hence it's necessary to set NODE_PATH
```bash
export NODE_PATH=$(npm root --quiet -g)
```

## node_modules bin dir
```
/home/node/app/node_modules/.bin
```

# typescript

## better tsc config options for writing ts files to be used as js for the browser
```json
{
    "compilerOptions": {
        "target": "ES2017",
        "module": "ES6",
        "outDir": ".", // <- creates JS for all TS in the pwd
        "rootDir": ".",
        "sourceMap": false,
        "noEmit": false
    }
}
```
```ts
// order.ts
import { create_toast, show_toast } from "./utils.js"  // <- use ".js" instead of no extension like normal ts modules
...

// util.ts
document.addEventListener("DOMContentLoaded", function (e) {  // <- this works just fine!
    // blah blah
});

```

- https://gist.github.com/khansgithub/c7a6bfca57631a4c45e2c75b7b5f881e#transpile-multile-ts-files

## transpile multile ts files
```typescript
/***
app/
    - tsconfig.json
    src/
        - index.ts
        - front/
            - tsconfig.json
            - foo.ts
***/

// app/src/tsconfig.json
{
    "compilerOptions": {
        "noEmit": true
    },
    "include": ["./src/**/*.ts"],
    "exclude": ["**/node_modules/*", "./src/front/**/*"]
}

// app/src/front/tsconfig.json
{
    "compilerOptions": {
        "noEmit": false
    },
    "include": ["*.ts"],
    "exclude": [] // <- this was important!
}

// tsc with build option from /app/
tsc -b . ./src/front
```

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

## dynamic (hacky??) type guard
```typescript
function identify<Type>(arg: unknown, field: string): arg is Type {
    return (arg as any)[field] !== undefined;
}

identify<Piece>(square, "piece_type")
```

## `this` can be typehinted in the function signature, useful when using with `bind`
```typescript
class Foo{
    public foobar = function(this: Bar){
        this.print_bar() // ts understands `this` is typeof Bar
    }.bind(new Bar())
}
const foo = new Foo()
foo.foobar()
// -> "bar"
```



## debug in vscode
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

# stupid front end stuff

## appending innerHTML breaks all event listeners
```js
var html_to_insert = "<p>New paragraph</p>";

// with .innerHTML, destroys event listeners
document.getElementById('mydiv').innerHTML += html_to_insert;

// with .insertAdjacentHTML, preserves event listeners
document.getElementById('mydiv').insertAdjacentHTML('beforeend', html_to_insert);
```

# vs code

## custom tasks
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

## set `imagePullPolicy` to `Always`, then delete the pod, to easily update the pod with a newer image

## restart deployment
```bash
kubectl rollout restart deployment/core-service  -n osna 
```

# kotlin
## null saftey expression
```kotlin
// typescript -> if (isTypeFoo()) doFooStuf()
// kotlin:
foo?.let { doFooStuff() }
```

## kotlin vscode tasks
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

# android 

## get the SHA1 signature
```bash
keytool -list -v -keystore C:\Users\%USERNAME%\.android\debug.keystore -alias androiddebugkey -storepass android -keypass android
```

## when using `by` for property delegation with `collectAsState`, there will be an error unless you import `import androidx.compose.runtime.getValue`
```kotlin
import androidx.compose.runtime.getValue

// ...

val navTarget by navVM.navTarget.collectAsState(initial = "home")
// without getValue import: 
// Type 'androidx. compose. runtime. State<kotlin. Any?>' has no method 'getValue(Nothing?, KProperty0<*>)', so it cannot serve as a delegate.
```

# bash

## switch user and choose which shell to use
```bash
su -s /bin/bash <user>
```


## retain environment variables when using sudo
```bash
sudo -E foobar
```

## check if a folder exists using the `test` commands
```bash
if test -d cisco_bindings; then echo exists; else echo does not; fi
```

# css

## position a `position: absolute` element inside a `relative`
```
.foo
  .bar
  .bar2
  .bar3
```
```
body{
  background: black;
}

div{ width: 100px; height: 100px; border: 1px solid white;}

.foo{
  width: 80%;
  display: flex;
  position: relative; /* this is crucial! default is `static` _not_ `relative` */
}

.bar{
  background: lightgrey;
  position: absolute;
  right: 0;
}
```

## prevent an element from exceeding the screen and ever overflowing
```css
body{
    max-height: 99vh;
}
```

## use `pointer-events: none` to disable mouse events of an element. can be useful when two elements are stacked on top of each other, and you want to allow the events of the element beneath through
```html
<div id="foo"> 
  <p>foo</p>
</div>
<div id="bar">
  <p>bar</p>
</div>
```
```css
#foo{
  position: absolute;
  background: red;
  width: 100px;
  height: 100px;
  left: 50px;
  top: 50px;
  color: black;
  text-align: right;
}

#bar{
  position: absolute;
  background: blue;
  width: 100px;
  height: 100px;
  color: white;
  text-align: right;
  pointer-events: none; /* click + hover are disabled for this */
}
```
```typescript
let foo = document.getElementById("foo") as HTMLElement;
let bar = document.getElementById("bar") as HTMLElement;

foo.addEventListener("mouseover", e => console.log("foo hover")});
foo.addEventListener("click", e => console.log("foo click")});

bar.addEventListener("mouseover", e => console.log("bar hover")});
bar.addEventListener("click", e => console.log("bar click")});
```

## feathered clipping mask
```css
background:
	var(--noise), /* url("noise svg here") */
	radial-gradient(circle at center, rgb(255,255,255) 0%, rgba(0,0,0,1) 50%);
background-size: cover;	
background-blend-mode: multiply;
mix-blend-mode: screen;
```

# misc

## devtools
hide error in dev tools window
```
-net::ERR_BLOCKED_BY_CLIENT
```

## alternate values like the squares on a chess board, if you have indices for x + y (row and column)
```typescript
x&1 ^ y&1 ? true : false

/***
x&1 -> odd or even row/column
y&1 -> odd of even square

x&1 0 0 1 1 
y&1 0 1 0 1
XOR 0 1 1 0

the first cell of an odd row, must be the same as the first cell of an even row, for a chequered pattern.

0 1 0 1
1 0 1 0
***/
```

## installing on corp VM
```bash
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

## Microsoft Tunnels
### steps to install tunnels
```bash
wget -O vscode_cli.tar.gz 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' && tar -xzf vscode_cli.tar.gz -C /opt

chmod +x /opt/code
cd opt
./code tunnel

# install Microsoft: Tunnels
# Remote-Tunnels: Connect to Tunnel
```

# organise later
```bash
# get current deployment config
kubectl get deployment osnal2 n osna -o yaml > deployment.yaml

# patch deployment
kubectl apply -f  deployment.yaml 

# push to pod
kubectl cp "/home/ubuntu/osna/osna-l2-main/osna-l2/producer.py" "osna/osnal2-f458bd694-hl4tj:/app"
kubectl cp "/home/ubuntu/osna/osna-l2-main/osna-l2" "osna/$(kubectl get pods | grep l2 | awk '{print $1}'):/app"

# kill all BASH processes except current
ps -C bash -o pid= | grep -v "^ *$$" | xargs kill -9 

# poetry image
## Dockerfile
from python:3.11-slim

env PATH="/root/.local/bin:${PATH}"
run bash -c "pip install --user pipx && \
    pipx ensurepath && \
    pipx completions && \
    pipx install poetry"

## docker-compose.yaml
services:
  python-poetry:
    build:
      context: .
      dockerfile: Dockerfile
    image: python-poetry:latest
```

# rust

## a `reference` and `pointer` are not the same thing (i think)
```rust
// https://ntietz.com/blog/rust-references-vs-pointers/
fn main() {
    let x: u32 = 10;
    let ref_x: &u32 = &x;
    let pointer_x: *const u32 = &x;

    println!("x: {x}");
    println!("ref_x: {}", ref_x);
    println!("pointer_x: {:?}", pointer_x);
}
```

# sql
## lint sql
```bash
# apt install pipx
# pipx install sqlfluff
sqlfluff lint --dialect postgres schema.ql
```

# svelte
## spa
```bash
npm create vite@latest
npm i --save-dev @tsconfig/svelte
./tsconfig.node.json: $.compilerOptions.noEmit > $.compilerOptions.emitDeclarationOnly // https://stackoverflow.com/a/77369498
```

## use `{@const}` to create in-template variables, also works with reactive states (but you cannot create reactive states i.e. $state rune, in the directive
```svelte
{@const square: Piece | Empty = g.get(...}
{@const marked = !isPiece(square) ? square.is_marked() : null}
<div class="{marked ? 'marked' : null}"></div>
```

## getting vitest set up (fucking pita)
```bash
# run in project
npx sv add vitest

mv test src/
```

# vue
## smooth fade animation that doesn't snap between transitions
```vue
<script setup>
  const classes = ref({
    fadeIn: false,
    fadeOut: false,
  });
  const elem = ref(null);
  const opacityValue = ref(0.0);
  
  function enter() {
    classes.value.animationPause = true;

    classes.value.fadeOut = false

    opacityValue.value = getCurrentOpacity();;
    classes.value.fadeIn = false;
    classes.value.fadeIn = true;

    classes.value.animationPause = false;
  }

  function leave() {
    classes.value.animationPause = true;

    classes.value.fadeIn = false;
    opacityValue.value = getCurrentOpacity();

    classes.value.fadeOut = false;
    classes.value.fadeOut = true;

    classes.value.animationPause = false;
  }
  function getCurrentOpacity() {
    let elem = elem.value as unknown as HTMLElement;
    let elem_styles = window.getComputedStyle(elem);
    return parseFloat(elem_styles.opacity)
  }
</script>

<template>
  <div 
    @mouseenter="e => enter()}"
    @mouseleave="e => leave()"
    :class="classes"
    :ref="elem"
  >

  </div>
</template>

<style>
div {
  opacity: 0;
}
.fadeIn {
  animation: fade-in 0.5s;
  animation-fill-mode: forwards;
}

.fadeOut {
  animation: fade-out 0.5s;
  animation-fill-mode: forwards;
}

.animationPause{
  animation-play-state: paused;
}

@keyframes fade-in {
  from {
    opacity: v-bind("opacityValue")
  }

  to {
    opacity:1;
  }
}

@keyframes fade-out {
  from {
    opacity: v-bind("opacityValue");
  }

  to {
    opacity: 0;
  }
}
</style>
```

# web
## using `filter` encapsulates a `position:fixed` object in a block, making its position **relative** to that invisible block, and **not relative to the window**
- https://stackoverflow.com/a/52937920
