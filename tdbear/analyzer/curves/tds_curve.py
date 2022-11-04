from __future__ import annotations
from typing import Iterator, Iterable, Self, Any
import operator
import itertools
import functools
import warnings

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.figure as figure

from ..._util import Float64Array
from ..labels import Labels
from .curve import Curve


class TDSCurve(Curve):
    """# `tdbear.analyzer.TDSCurve`

    A class representing time-series data of TDS trials.
    """

    __cache = {}

    @staticmethod
    def from_dict(dic: dict, resolution: int = 1000) -> TDSCurve:
        timing_data: dict[str, list[float]] = dic["data"]
        duration: float = dic["duration"]
        delay: float = max(itertools.chain.from_iterable(timing_data.values()))
        attr_nums: Labels = Labels.get_instance(sorted(timing_data))

        data: Float64Array = np.zeros((len(attr_nums) + 1, resolution), np.float64)
        meta: dict[str, list[Any]] = dic["meta"]

        r = resolution / duration
        times: list[tuple[int, int]] = [
            (attr_nums[attr], round(t * r))
            for attr in timing_data
            for t in timing_data[attr]
        ]

        times.sort(key=operator.itemgetter(1))

        times.append((-1, resolution))

        data[-1, : times[0][1]] = 1.0

        for (a, b) in itertools.pairwise(times):
            data[a[0], a[1] : b[1]] = 1.0

        return TDSCurve(attr_nums, [duration], [delay], data, meta)

    @classmethod
    def sum(cls, args: Iterable[Self]) -> Self:
        it: Iterator[Self] = iter(args)
        first: Self = next(it)
        durations: list[float] = [*first.durations]
        delays: list[float] = [*first.delays]
        meta: dict[str, list[Any]] = {k: [*v] for (k, v) in first.meta.items()}
        data: Float64Array = first.data * first.trials_count
        buff: Float64Array = np.empty(data.shape, float)

        warn = functools.partial(warn_if_meta_dismatch, {*first.meta})

        for elem in it:

            check_operable(first, elem)
            warn(elem)

            for key in {*itertools.chain(first.meta, elem.meta)}:
                meta[key] += elem.meta[key]

            durations += elem.durations
            delays += elem.delays

            np.multiply(elem.data, elem.trials_count, buff)
            np.add(data, buff, data)

        np.divide(data, data.sum(0), data)

        name: str
        if "ASSESSOR" in first.meta:
            name = (
                f'{first.meta["ASSESSOR"][0]} and '
                f"{sum(a.trials_count for a in args) - 1} others"
            )
        else:
            name = f"{sum(a.trials_count for a in args)} trials"

        return TDSCurve(first.attr_nums, durations, delays, data, meta, name).fix()

    @property
    def trials_count(self) -> int:
        return len(self.durations)

    @property
    def average_duration(self) -> float:
        return np.mean(self.durations, dtype=float)

    @property
    def average_delay(self) -> float:
        return np.mean(self.delays, dtype=float)

    def __init__(
        self,
        attr_nums: Labels,
        durations: list[float],
        delays: list[float],
        data: Float64Array,
        meta: dict[str, list[Any]],
        name: str | None = None,
    ):

        self.attr_nums = attr_nums
        self.data = data
        self.meta = meta
        self.name = name or "No Name"

        self.durations: list[float] = durations
        self.delays: list[float] = delays

    def __add__(self, other: Self) -> Self:
        return TDSCurve.sum((self, other))

    def __radd__(self, other: Self) -> Self:
        return other + self

    def __abs__(self) -> int:
        return self.trials_count

    def __repr__(self) -> str:
        return (
            f"[TDSCurve of {self.trials_count} "
            f'trial{"" if self.trials_count <= 1 else "s"}]'
        )

    def distance(self, other: Self) -> float:
        check_operable(self, other)
        return np.mean((((self.data - other.data) ** 2).sum(0) / 2) ** 0.5, dtype=float)

    def draw(
        self,
        layout: list[list[list[str]]] | None = None,
        time_denominator: float = 1.0,
        proportion_denominator: float = 1.0,
        show: bool = True,
        show_chance: bool = True,
        show_signif: bool = True,
        show_total: bool = False,
        show_delay: bool = False,
        show_average_delay: bool = False,
        show_legend: bool = True,
        curve_args: dict[str, Any] = {},
        chance_args: dict[str, Any] = {},
        signif_args: dict[str, Any] = {},
        total_args: dict[str, Any] = {},
        delay_args: dict[str, Any] = {},
        average_delay_args: dict[str, Any] = {},
        legend_args: dict[str, Any] = {},
    ) -> tuple[figure.Figure, list[list[plt.Axes]]]:

        if layout is None:
            layout = [[[*self.attr_nums]]]

        rows: int = len(layout)
        columns: int = max(map(len, layout))
        axes: list[list[plt.Axes]] = [[]] * rows
        ax_number: int = 1
        time_ax: Float64Array = np.concatenate(
            [
                np.arange(0, self.resolution) / self.resolution * time_denominator,
                np.array([time_denominator]),
            ]
        )

        fig: figure.Figure = plt.figure()
        fig.suptitle(self.name)

        for (i, row) in enumerate(layout):
            for (j, column) in enumerate(row):
                ax: plt.Axes = fig.add_subplot(
                    rows,
                    columns,
                    ax_number,
                    xlabel="Normalized Time",
                    ylabel="Dominance Proportion",
                )

                axes[i].append(ax)

                ax_number += 1

                # TDS curves
                attr_count: int = 1
                for key in column:
                    data: Float64Array = np.concatenate([np.array([0.0]), self(key)])

                    style: str = "dashed" if attr_count > 10 else "solid"

                    axes[i][j].plot(
                        time_ax,
                        data * proportion_denominator,
                        **{"label": key, "linestyle": style, **curve_args},
                    )

                    attr_count += 1

                # graph parameters
                chance: float = 1 / len(self.attr_nums)
                signif: float = (
                    chance
                    + 1.64485362695145
                    * (chance * (1 - chance) / self.trials_count) ** 0.5
                )

                # plot graph parameters
                if show_chance:
                    axes[i][j].plot(
                        (0, time_denominator),
                        (chance * proportion_denominator,) * 2,
                        **{
                            "label": "Chance",
                            "linestyle": "dotted",
                            "color": "gray",
                            **chance_args,
                        },
                    )

                if show_signif:
                    axes[i][j].plot(
                        (0, time_denominator),
                        (signif * proportion_denominator,) * 2,
                        **{
                            "label": "Signif.",
                            "linestyle": "dashed",
                            "color": "gray",
                            **signif_args,
                        },
                    )

                if show_total:
                    total = sum(map(self, column))

                    y = np.concatenate(
                        [np.array([1.0]), total + self.delay_proportion]
                        if show_delay
                        else [np.array([0.0]), total]
                    )

                    axes[i][j].plot(
                        time_ax,
                        y * proportion_denominator,
                        **{"label": "Total", "linestyle": "dashed", **total_args},
                    )

                if show_delay:
                    y = np.concatenate([np.array([1.0]), self.delay_proportion])

                    axes[i][j].plot(
                        time_ax,
                        y * proportion_denominator,
                        **{"label": "Delay", "linestyle": "dashed", **delay_args},
                    )

                if show_average_delay:
                    average_delay: float = (
                        np.mean(self.delay_proportion, dtype=float) * time_denominator
                    )

                    p: float

                    if show_delay:
                        p = 1.0

                    elif show_total:
                        s = sum(map(self, column))

                        if isinstance(s, np.ndarray):
                            p = max(s)
                        else:
                            p = s
                    else:
                        p = max(max(self(key).max() for key in column), chance, signif)

                    axes[i][j].plot(
                        (average_delay, average_delay),
                        (0, p * proportion_denominator),
                        **{
                            "label": "Average Delay",
                            "linestyle": "dashdot",
                            "color": "gray",
                            **average_delay_args,
                        },
                    )

                if show_legend:
                    axes[i][j].legend(**legend_args)

        # show graph or not
        if show:
            plt.show()

        return (fig, axes)


def check_operable(left: TDSCurve, right: TDSCurve) -> None:
    if left.attr_nums != right.attr_nums:
        raise ValueError(
            "Different formats are mixed. " "Please review attribute words."
        )

    elif left.resolution != right.resolution:
        raise ValueError(
            "Data of different lengths are mixed. " 'Please review "resolution" field.'
        )


def warn_if_meta_dismatch(left: set[str], right: TDSCurve) -> None:
    if left != {*right.meta}:
        warnings.warn(
            "Metadata of different types are mixed. " 'Please review "meta" field.',
            Warning,
        )
