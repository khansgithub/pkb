import json
import logging
from functools import partial
from typing import Callable
from urllib.parse import urljoin

import requests

logging.basicConfig(level=logging.INFO)


class Routes:
    health = "health"
    sync = "sync"
    search = "search"


def base(
    root: str, endpoint: str, method: Callable, json: dict = {}
) -> requests.Response:
    return method(url=urljoin(root, endpoint), json=json)


base_url = "localhost:8000"
base_req = partial(base, root="http://" + base_url)


def health() -> requests.Response:
    return base_req(endpoint=Routes.health, method=requests.get)


def sync() -> requests.Response:
    return base_req(endpoint=Routes.sync, method=requests.post)


def search() -> requests.Response:
    search_term = {"term": "git"}
    logging.info(f"{search_term=}")
    return base_req(endpoint=Routes.search, method=requests.post, json=search_term)


f = [
    # health,
    sync,
    search,
]

for func in f:
    print("Running: ", func.__name__)
    res = func().json()
    res_json = json.dumps(res, indent=4)

    # print(res_json)

    if res.get("results"):
        for r in res["results"]:
            print("#################################")
            code = r["metadata"].get("code")
            print(code)
            print("#################################")
