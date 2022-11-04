from __future__ import annotations
from typing import Iterable, Iterator, Self, overload
from functools import cache


class Labels:
    """# `tdbear.analyzer.Labels`"""

    @classmethod
    def get_instance(cls, labels: Iterable[str], /) -> Self:
        return cls.__get_instances(labels if isinstance(labels, tuple) else (*labels,))

    @classmethod
    @cache
    def __get_instances(cls, keys: tuple[str, ...], /) -> Self:
        return cls(keys)

    def __init__(self, keys: tuple[str, ...], /):

        self.__keys: tuple[str, ...] = keys
        self.__vals: dict[str, int] = dict(zip(keys, range(len(keys))))

    @overload
    def __getitem__(self, key: str, /) -> int:
        ...

    @overload
    def __getitem__(self, key: int, /) -> str:
        ...

    def __getitem__(self, key, /):
        if isinstance(key, str):
            return self.__vals[key]
        else:
            return self.__keys[key]

    def __iter__(self, /) -> Iterator[str]:
        return self.__vals.__iter__()

    def __len__(self, /) -> int:
        return len(self.__vals)

    def __eq__(self, other: Self, /) -> bool:
        return other.__keys == self.__keys

    def __ne__(self, other: Self, /) -> bool:
        return not (self.__keys == other.__keys)

    def __repr__(self, /) -> str:
        return self.__vals.__repr__()
