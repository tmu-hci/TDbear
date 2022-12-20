from __future__ import annotations as __anotations
from typing import (
    Callable,
    Iterable,
    overload,
)

import itertools

import numpy as np
from sklearn import decomposition

from ..._util import Float64Array
from ..curves import TDSCurve
from ..labels import Labels
from .pca_result import PCAResult


class PCA:
    """# `tdbear.analyzer.PCA`"""

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

    @staticmethod
    def default_data_extractor(curve: TDSCurve) -> Float64Array:
        return curve.dominance_duration[:-1]

    def fit(
        self,
        tds_curves: Iterable[TDSCurve],
        *,
        # default data extractor uses dominance duration
        # for each attribute without delay
        data_extractor: Callable[[TDSCurve], Iterable[float]] = default_data_extractor,
        standardize: bool = True,
        labels: Labels | None = None,
    ) -> PCAResult:

        result = PCAResult()
        result.tds_curves = (*tds_curves,)

        data: Float64Array = np.array([*map(data_extractor, result.tds_curves)])

        nonzero_index = np.array(~np.isclose(data.sum(0), 0.0))

        if labels is None:
            result.labels = result.tds_curves[0].attr_nums
        else:
            result.labels = labels

        result.labels = Labels((*itertools.compress(result.labels, nonzero_index),))
        data = data[:, nonzero_index]

        if standardize:
            data = (data - data.mean(0)) / data.std(0)

        result.scores = self.model.fit(data).transform(data).T
        result.components = getattr(self.model, "components_")
        result.variance = getattr(self.model, "explained_variance_")
        result.variance_ratio = getattr(self.model, "explained_variance_ratio_")
        result.singular_values = getattr(self.model, "singular_values_")

        return result
