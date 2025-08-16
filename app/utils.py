from typing import overload


def debug():
    import ipdb

    ipdb.set_trace()


# index = dict[str | int, str | int]


class Index(dict):
    """
    [1] - level 1 heading
    [2] - level 2 heading etc...
    last() - the deepest heading
    """

    _last = "_last"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self[self._last] = 0

    def last(self, v: int | None = None) -> int:
        """
        sets the number of the last heading if given.
        returns the depth of the current section.
        """
        if v is not None:
            self[self._last] = v
        return self[self._last]

    @overload
    def __getitem__(self, key: str) -> int: ...

    @overload
    def __getitem__(self, key: int) -> str: ...

    def __getitem__(self, key: int | str) -> int | str:
        return super().__getitem__(key)
