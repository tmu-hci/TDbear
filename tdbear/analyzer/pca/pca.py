from __future__ import annotations as __anotations
from typing import Callable, Iterable, overload

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

        self.model: decomposition.PCA
        self.tds_curves: tuple[TDSCurve, ...] = tuple()
        self.labels: Labels = Labels.get_instance([])

        if isinstance(arg1, int):
            self.model = decomposition.PCA(arg1)
        else:
            self.model = arg1

    def fit(
        self,
        tds_curves: Iterable[TDSCurve],
        *,
        data_extractor: Callable[
            [TDSCurve], Iterable[float]
        ] = lambda e: e.dominance_duration[:-1],
        standardize: bool = True,
        labels: Labels | None = None,
    ) -> PCAResult:

        result = PCAResult()
        result.tds_curves = (*tds_curves,)

        if labels is None:
            result.labels = result.tds_curves[0].attr_nums
        else:
            result.labels = labels

        data: Float64Array = np.array([*map(data_extractor, result.tds_curves)])

        if standardize:
            data = (data - data.mean(0)) / data.std(0)

        result.scores = self.model.fit(data).transform(data).T
        result.components = getattr(self.model, "components_")
        result.variance = getattr(self.model, "explained_variance_")
        result.variance_ratio = getattr(self.model, "explained_variance_ratio_")
        result.singular_values = getattr(self.model, "singular_values_")

        return result
