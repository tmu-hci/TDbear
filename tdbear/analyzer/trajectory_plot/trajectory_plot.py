from __future__ import annotations as __anotations
from typing import (
    Callable,
    Iterable,
    overload,
)

import numpy as np
import matplotlib.pyplot as plt
from sklearn import decomposition

from ..._util import Float64Array
from ..curves import TDSCurve
from ..labels import Labels
from .trajectory_plot_result import TrajectoryPlotResult


class TrajectoryPlot:
    """# `tdbear.analyzer.TrajectoryPlot`"""

    @overload
    def __init__(self, n_components: int = 2, /):
        ...

    @overload
    def __init__(self, model: decomposition.PCA, /):
        ...

    def __init__(self, arg1: int | decomposition.PCA = 2, /):

        self.model: decomposition.PCA = (
            decomposition.PCA(arg1) if isinstance(arg1, int) else arg1
        )
        self.tds_curves: tuple[TDSCurve, ...] = ()
        self.labels: Labels = Labels.get_instance([])

    def fit(
        self,
        tds_curve: TDSCurve,
    ) -> TrajectoryPlotResult:

        result = TrajectoryPlotResult()
        result.tds_curve = tds_curve

        data = tds_curve.data[:-1].T
        data = (data - data.mean(0)) / data.std(0)

        result.scores = self.model.fit(data).transform(data).T
        components = getattr(self.model, "components_")
        # result.variance = getattr(self.model, "explained_variance_")
        # result.variance_ratio = getattr(self.model, "explained_variance_ratio_")
        # result.singular_values = getattr(self.model, "singular_values_")

        plt.plot(result.scores[0], result.scores[1])
        for (k, c) in enumerate(components.T):
            plt.plot(
                (0, c[0]),
                (0, c[1]),
                **{
                    "label": tds_curve.attr_words[k]
                    if k < len(tds_curve.attr_words)
                    else "delay"
                },
            )
        plt.legend()
        plt.show()
        return result
