from __future__ import annotations
from io import TextIOWrapper
from typing import (
    Callable,
    Hashable,
    Iterable,
    SupportsIndex,
    Sequence,
    Self,
    Any,
    overload,
)
import random
import itertools
import functools

import yaml
import matplotlib.pyplot as plt
import matplotlib.figure as figure

from .tds_curve import TDSCurve


class TDSContainer(list[TDSCurve]):
    """# `tdbear.analyzer.TDSContainer`"""

    @staticmethod
    def from_yaml(yml: str | TextIOWrapper, resolution: int = 1000) -> TDSContainer:
        """# `tdbear.analyzer.TDSContainer.from_yaml()`

        Creates a new `TDSContainer` instance from a YAML string.
        The YAML string must be in the format
        in which TDSampler outputs.

        ## Args
        - `yml`        : YAML string
        - `resolution` : Number of discretized interval of the entire
                         duration (start to stop). Defaults to `1000`.

        ## Returns
        - `TDSContainer` : A list-like object that contains multiple
                           `TDSCurve` objects.

        ## Throws
        - `ValueError` : Thrown then the generated time-series data seems
                         to be corrupted.

        ## Examples
        ```python
        import tdbear.analyzer as ta

        with open("./nanakoberry/PA/PA.yml", "r", encoding="UTF-8") as f:
            csv = f.read()
            curves = ta.TDSContainer.from_yaml(csv)
        ```
        """

        records = yaml.safe_load_all(yml)

        return TDSContainer(
            map(functools.partial(TDSCurve.from_dict, resolution=resolution), records)
        )

    def __or__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*self} | {*other})

    def __ror__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*other} | {*self})

    def __and__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*self} & {*other})

    def __rand__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*other} & {*self})

    def __xor__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*self} ^ {*other})

    def __rxor__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*other} ^ {*self})

    def __add__(self, other: Iterable[TDSCurve], /) -> Self:
        if not isinstance(other, list):
            other = list(other)

        return TDSContainer(list.__add__(self, other))

    def __radd__(self, other: Iterable[TDSCurve], /) -> Self:
        if not isinstance(other, list):
            other = list(other)

        return TDSContainer(list.__add__(other, self))

    def __sub__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*self} - {*other})

    def __rsub__(self, other: Iterable[TDSCurve], /) -> Self:
        return TDSContainer({*other} - {*self})

    def __mul__(self, other: SupportsIndex, /) -> Self:
        return TDSContainer(super().__mul__(other))

    def __mod__(self, other: TDSCurve, /) -> Self:
        return TDSContainer({*self} - {other})

    def __pow__(self, other: Iterable[Any], /) -> Iterable[tuple[TDSCurve, Any]]:
        return itertools.product(self, other)

    def __rpow__(self, other: Iterable[Any], /) -> Iterable[tuple[Any, TDSCurve]]:
        return itertools.product(other, self)

    def __matmul__(self, func: Callable[[Self], Any], /) -> Any:
        return func(self)

    def __rshift__(self, func: Callable[[TDSCurve], Any], /) -> list[Any]:
        return [*map(func, self)]

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> TDSCurve:
        ...

    @overload
    def __getitem__(self, index: slice, /) -> Self:
        ...

    def __getitem__(self, index, /):
        value = super().__getitem__(index)

        if isinstance(value, list):
            return TDSContainer(value)
        else:
            return value

    @overload
    def __setitem__(self, index: SupportsIndex, value: TDSCurve, /) -> None:
        ...

    @overload
    def __setitem__(self, index: slice, value: Iterable[TDSCurve], /) -> None:
        ...

    def __setitem__(self, index, value, /):
        super().__setitem__(index, value)

    def __repr__(self, /) -> str:
        n: int = self @ abs
        return (
            f"[TDSContainer of {self @ len} TDSCurve "
            f'({n} trial{"" if n <= 1 else "s"})]'
        )

    def __abs__(self, /) -> int:
        return sum(x.trials_count for x in self)

    def copy(self, /) -> Self:
        return TDSContainer(super().copy())

    def map(self, func: Callable[[TDSCurve], TDSCurve]) -> Self:
        return TDSContainer(map(func, self))

    def filter(self, func: Callable[[TDSCurve], bool]) -> Self:
        return TDSContainer(filter(func, self))

    def group_by(
        self, func: str | Callable[[TDSCurve], Hashable]
    ) -> dict[Hashable, Self]:

        result: dict[Hashable, TDSContainer] = {}
        group_func: Callable[[TDSCurve], Hashable]

        if isinstance(func, str):

            def _group_func(x: TDSCurve):
                return x.get_meta(func)

            group_func = _group_func

        else:
            group_func = func

        for curve in self:
            key = curve @ group_func

            if key not in result:
                result[key] = TDSContainer()

            result[key].append(curve)

        return result

    def order_by(self, func: str | Callable[[TDSCurve], Any], desc=False) -> Self:

        order_func: Callable[[TDSCurve], Any]

        if isinstance(func, str):

            def _order_func(x: TDSCurve):
                return x.get_meta(func)

            order_func = _order_func

        else:
            order_func = func

        self.sort(key=order_func, reverse=desc)

        return self

    def get_meta(self, key: str) -> list[Any]:
        return self >> (lambda e: TDSCurve.get_meta(e, key))

    def get_meta_all(self, key: str) -> list[list[Any]]:
        return self >> (lambda e: TDSCurve.get_meta_all(e, key))

    def set_meta(self, key: str, value: Any) -> Self:
        for curve in self:
            curve.set_meta(key, value)

        return self

    def set_meta_all(self, key: str, value: list[Any] | None) -> Self:
        for curve in self:
            curve.set_meta_all(key, value)

        return self

    def merge(self) -> TDSCurve:
        return TDSCurve.sum(self)

    def merge_as(self, name: str) -> TDSCurve:
        return self.merge().set_name(name)

    def bootstrap(self, size: int | None = None) -> Self:
        k: int = self @ len if size is None else size

        return TDSContainer(random.choices(self, k=k))

    def distance(
        self, distance_func: Callable[[TDSCurve, TDSCurve], float] = TDSCurve.distance
    ) -> list[float]:

        merged = self.merge()

        return self >> (lambda x: distance_func(x, merged))

    def box_plot(
        self,
        map_func: Callable[[Self], Sequence[float]] = distance,
        boxplot_args: dict[str, Any] = {},
        scatter_args: dict[str, Any] = {},
        show_scattter: bool = True,
        scatter_position: float = 1.0,
        vertical: bool = True,
        show: bool = True,
    ) -> tuple[figure.Figure, plt.Axes]:

        data: Sequence[float] = self @ map_func

        fig: figure.Figure = plt.figure()

        fig.suptitle("Box Plot")

        ax: plt.Axes = fig.add_subplot()

        ax.boxplot(data, **{**boxplot_args, "vert": vertical})

        x = (scatter_position,) * len(self)
        y = data

        if not vertical:
            [x, y] = [y, x]

        if show_scattter:
            ax.scatter(x, y, **scatter_args)

        if show:
            plt.show()

        return (fig, ax)
