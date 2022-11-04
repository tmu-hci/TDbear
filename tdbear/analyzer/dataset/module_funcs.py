from importlib.resources import files

from ... import analyzer
from ..._util import Console
from ..curves.tds_container import TDSContainer


def load_nanakoberry(
    *, resolution: int = 1000, print_status: bool = True
) -> TDSContainer:
    """# `tdbear.analyzer.dataset.load_nanakoberry()`"""

    file = files(analyzer).joinpath("dataset/nanakoberry.yml")

    if print_status:
        Console.log(("Loading ", Console.CYAN), ('"nanakoberry"', Console.MAGENTA))

    with file.open("r", encoding="UTF-8", newline="\n") as f:
        return TDSContainer.from_yaml(f, resolution)
