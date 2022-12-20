"""# `tdbear.analyzer`
"""

import matplotlib.pyplot as __plt

from ..analyzer.labels import Labels
from ..analyzer.curves import Curve, TDSCurve, TDSContainer
from ..analyzer.analysis_result import AnalysisResult
from ..analyzer.pca import PCA, PCAResult
from ..analyzer.trajectory_plot import TrajectoryPlot, TrajectoryPlotResult
from ..analyzer.module_funcs import load_file, load_dir, repl, show

from . import dataset


# add some font parameters to matplotlib
__plt.rcParams["font.sans-serif"][0:0] = (
    "Roboto",
    "Noto Sans JP",
    "Meiryo",
    "Yu Gothic",
    "MS Gothic",
    "Hiragino Sans",
)

__all__ = [
    #
    # module labels
    #
    "Labels",
    #
    # module curves
    #
    "Curve",
    "TDSCurve",
    "TDSContainer",
    #
    # module analysis_result
    #
    "AnalysisResult",
    #
    # module pca
    #
    "PCA",
    "PCAResult",
    #
    # module trajectory_plot
    #
    "TrajectoryPlot",
    "TrajectoryPlotResult",
    #
    # module module_funcs
    #
    "load_file",
    "load_dir",
    "repl",
    "show",
    #
    # module dataset
    #
    "dataset",
]
