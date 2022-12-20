from __future__ import annotations
from typing import Any

import matplotlib.pyplot as plt
import matplotlib.figure as figure

from ..analysis_result import AnalysisResult
from ..curves import TDSCurve
from ..labels import Labels

from ..._util import Float64Array


class TrajectoryPlotResult(AnalysisResult):

    tds_curve: TDSCurve
    scores: Float64Array
