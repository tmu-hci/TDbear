from __future__ import annotations
from typing import TypeVar, TypeAlias
import numpy as np


Float64Array: TypeAlias = "np.ndarray[int, np.dtype[np.float64]]"

T = TypeVar("T")
U = TypeVar("U")
