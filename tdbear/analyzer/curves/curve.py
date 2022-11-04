from __future__ import annotations
from typing import Any, Callable, Iterator, Self
import abc
import warnings

import numpy as np

from ..._util import T, Float64Array
from ..labels import Labels


class Curve(metaclass=abc.ABCMeta):
    """# `tdbear.analyzer.Curve`"""

    attr_nums: Labels
    data: np.ndarray[int, np.dtype[np.float64]]
    meta: dict[str, list[Any]]
    name: str

    @property
    def attr_words(self) -> tuple[str, ...]:
        return (*self.attr_nums,)

    @property
    def resolution(self) -> int:
        return self.data.shape[1]

    @property
    def delay_proportion(self) -> Float64Array:
        return self.data[-1]

    @property
    def normalized_delay(self) -> float:
        return np.mean(self.delay_proportion, dtype=float)

    @property
    def dominance_duration(self) -> Float64Array:
        return self.data.sum(1) / self.resolution

    def __eq__(self, other: Self) -> bool:
        return self is other

    def __ne__(self, other: Self) -> bool:
        return not (self == other)

    def __matmul__(self, func: Callable[[Self], T]) -> T:
        return func(self)

    def __rshift__(self, func: Callable[[Float64Array], Any]) -> Any:
        return func(self.data)

    def __getitem__(self, i: int | slice, /) -> Float64Array:
        return self.data[:, i]

    def __len__(self) -> int:
        return len(self.attr_nums)

    def __iter__(self) -> Iterator[str]:
        return self.attr_nums.__iter__()

    def __bool__(self) -> bool:
        return True

    def __hash__(self) -> int:
        return id(self)

    def __call__(self, *keys: str) -> Float64Array:
        key_count: int = len(keys)

        if key_count == 0:
            return self.data

        elif key_count == 1:
            return self.data[self.attr_nums[str(keys[0])]]

        else:
            return np.array([self.data[self.attr_nums[str(key)]] for key in keys])

    def at(
        self, normalized_time: float, include_delay: bool = False
    ) -> dict[str, float]:

        attrs: list[str] = sorted(self.attr_nums, key=lambda i: self.attr_nums[i])

        data: Float64Array

        if include_delay:
            attrs = [*attrs, "(DELAY)"]

        if not (0.0 <= normalized_time <= 1.0):
            raise ValueError("Normalized time must be " "in range [0.0, 1.0].")

        time = int(round(normalized_time * self.resolution) - 1)

        if time < 0:
            data = np.zeros(len(attrs), np.float64)
            data[-1] = 1.0

        else:
            data = self.data[:, time]

        return dict(zip(attrs, data))

    def attr_durations(self, include_delay=True) -> dict[str, float]:
        attr = (*self.attr_words, "(DELAY)") if include_delay else self.attr_words

        return dict(zip(attr, self.dominance_duration))

    def set_name(self, name: str = "No Name") -> Self:
        self.name = str(name)
        return self

    def set_meta(self, key: str, value: Any) -> Self:
        k: str = key.strip().upper()
        if k in self.meta:
            self.meta[k].insert(0, value)
        else:
            self.meta[k] = [value]
        return self

    def set_meta_all(self, key: str, value: list[Any] | None) -> Self:
        k: str = key.strip().upper()

        if value is None:
            del self.meta[k]
        else:
            self.meta[k] = value

        return self

    def get_meta(self, key: str) -> Any:
        key = key.strip().upper()
        meta: list = self.meta[key] if key in self.meta else []
        meta_len: int = len(meta)

        if not meta_len:
            warnings.warn(f'No metadata found for "{key}".', Warning)
        elif meta_len > 1:
            warnings.warn(f'Metadata for "{key}" has multiple values.', Warning)

        return meta[0] if meta_len else None

    def get_meta_all(self, key: str) -> list[Any]:
        key = key.strip().upper()
        meta: list = self.meta[key] if key in self.meta else []
        if not len(meta):
            warnings.warn(f'No metadata found for "{key}".', Warning)
        return meta

    def smooth(self, level: float = 0.01) -> Self:
        weight: int = int(level * self.resolution)
        edge: int = weight // 2
        rows: int = len(self.data)
        edged: Float64Array = np.concatenate(
            [
                np.tile(self.data[:, 0].reshape(rows, 1), edge),
                self.data,
                np.tile(self.data[:, -1].reshape(rows, 1), weight - edge - 1),
            ],
            1,
        )

        self.data = np.array(
            [np.convolve(row, [1 / weight] * weight, "valid") for row in edged]
        )

        return self

    def fix(self) -> Self:
        np.divide(self.data, self.data.sum(0), self.data)
        return self

    def resample(self, resolution: int, phase: float = 1.0) -> Self:
        width: int = self.resolution // resolution
        self.data = self.data[
            :, slice(min(int(width * phase), width - 1), self.resolution, width)
        ]
        return self

    def save(
        self,
        destination: str = ".",
        file_name: str = "untitled",
        file_extension: str = ".csv",
        delimiter: str = "\t",
        include_delay: bool = True,
    ) -> str:

        data: Float64Array = self.data if include_delay else self.data[:-1]
        data = data.round(4)

        if not file_name:
            file_name = self.name

        with open(
            f"{destination}/{file_name}{file_extension}",
            "w",
            encoding="UTF-8",
            newline="\n",
        ) as f:

            attrs = sorted(self.attr_nums, key=lambda i: self.attr_nums[i])

            result = (
                f"{delimiter.join(attrs)}"
                f'{delimiter + "DELAY" if include_delay else ""}\n'
                + "\n".join(delimiter.join(map(str, row)) for row in data.T)
                + "\n"
            )

            f.write(result)

        return result
