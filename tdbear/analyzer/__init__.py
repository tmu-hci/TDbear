"""# `tdbear.analyzer`
"""

import matplotlib.pyplot as __plt

from ..analyzer.labels import Labels
from ..analyzer.curves import Curve, TDSCurve, TDSContainer
from ..analyzer.analysis_result import AnalysisResult
from ..analyzer.pca import PCA
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
    "Labels",
    #
    "Curve",
    "TDSCurve",
    "TDSContainer",
    #
    "AnalysisResult",
    #
    "PCA",
    #
    "load_file",
    "load_dir",
    "repl",
    "show",
    #
    "dataset",
]
