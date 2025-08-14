import requests


class FailedGistRequestError(Exception):
    """Raised when a http request to get the raw gist fails"""

    gist_url: str
    response: requests.Response | None

    def __init__(
        self,
        gist_url: str,
        response: requests.Response | None = None,
        msg: str | None = None,
    ) -> None:
        self.gist_url = gist_url
        self.response = response
        super().__init__(msg)


class FailedGistParseError(Exception): ...


class FailedMarkdownParseErrorDocumen(Exception): ...


class MissingHeadingOne(FailedMarkdownParseErrorDocumen): ...
