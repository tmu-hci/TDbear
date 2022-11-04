from __future__ import annotations
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.figure as figure

from ..analysis_result import AnalysisResult
from ..curves import TDSCurve
from ..labels import Labels

from ..._util import Float64Array


class PCAResult(AnalysisResult):
    """# `tdbear.analyzer.PCAResult`"""

    tds_curves: tuple[TDSCurve, ...]
    labels: Labels
    scores: Float64Array
    components: Float64Array
    variance: Float64Array
    variance_ratio: Float64Array
    singular_values: Float64Array

    def draw(
        self,
        show: bool = True,
        show_scatter: bool = True,
        show_axes: bool = True,
        show_legend: bool = True,
        scatter_args: dict[str, Any] = {},
        axes_args: dict[str, Any] = {},
        legend_args: dict[str, Any] = {},
    ) -> list[tuple[figure.Figure, plt.Axes]]:

        g: list[tuple[figure.Figure, plt.Axes]] = []

        for i in range(len(self.scores) - 1):
            for j in range(i + 1, len(self.scores)):

                x: Float64Array = self.scores[i]
                y: Float64Array = self.scores[j]
                vr: Float64Array = self.variance_ratio

                fig: figure.Figure = plt.figure()
                ax: plt.Axes = fig.add_subplot(
                    xlabel=f"PC{i + 1} ({round(vr[i] * 100)}%)",
                    ylabel=f"PC{j + 1} ({round(vr[j] * 100)}%)",
                )

                fig.suptitle(f"PC{i + 1} and PC{j + 1}")

                if show_scatter:
                    ax.scatter(x, y, **scatter_args)

                if show_axes:
                    for (k, c) in enumerate(self.components.T):
                        ax.plot(
                            (0, c[0]),
                            (0, c[1]),
                            **{"label": self.labels[k], **axes_args},
                        )

                if show_legend:
                    ax.legend(**legend_args)

                g.append((fig, ax))

        if show:
            plt.show()

        return g
