from __future__ import annotations
from typing import Mapping, Any
import glob
import itertools

import matplotlib.pyplot as plt

from .._util import Console
from .curves import TDSContainer


def load_file(
    file_path: str, resolution: int = 1000, print_status: bool = True
) -> TDSContainer:
    """# `tdbear.analyzer.load_file()`

    Generates a TDSContainer object from a single file.
    The file must be in the format in which TDSampler outputs.

    ## Args
    - `file_path`    : File path including the extension.
    - `resolution`   : Number of discretized interval of the entire
                              duration (start to stop). Defaults to `1000`.
    - `print_status` : Set this `True` to indicate which file
                              is being loaded. Defaults to `True`.

    ## Returns
    - `TDSContainer` : A list-like object that contains multiple
                       `TDSCurve` objects.

    ## Throws
    - `OSError` : Thrown when an error occurs while opening the file.

    ## Examples
    ```python
    import tdbear.analyzer as ta

    dataset = ta.load_file("./nanakoberry/PA/PA1.yml")
    ```
    """

    file_path = file_path.replace("\\", "/")

    if print_status:
        Console.log(("Loading ", Console.CYAN), (f'"{file_path}"', Console.MAGENTA))

    with open(file_path, "r", encoding="UTF-8", newline="\n") as f:
        return TDSContainer.from_yaml(f, resolution)


def load_dir(
    dir_path: str = ".",
    file_extension: str = ".yml",
    resolution: int = 1000,
    print_status: bool = True,
) -> TDSContainer:
    """# `tdbear.analyzer.load_dir()`

    Generates a TDSContainer object from files in the specified directorys(s).
    All files must be in the format in which TDSampler outputs.

    ## Args
    - `dir_path`       : Directory path (not the file path).
                         You can use glob pattern. Defaults to ".".
    - `file_extension` : File extension. Defaults to ".yml".
    - `resolution`     : Number of discretized interval of the entire
                         duration (start to stop). Defaults to `1000`.
    - `print_status`   : Set this `True` to indicate which file
                         is being loaded. Defaults to `True`.

    ## Returns
    - `TDSContainer` : A list-like object that contains multiple
                       `TDSCurve` objects.

    ## Throws
    - `FileNotFoundError` : Thrown when no file is found.
    - `OSError`           : Thrown when an error occurs while opening the file.

    ## Examples
    ```python
    import tdbear.analyzer as ta

    dataset = ta.load_dir("./nanakoberry/**/")
    ```
    """

    dir_path = dir_path.replace("\\", "/")

    if print_status:
        Console.log(("Loading ", Console.CYAN), (f'"{dir_path}"', Console.MAGENTA))

    files: list = glob.glob(f"{dir_path}/*{file_extension}", recursive=True)

    obj: TDSContainer = TDSContainer(
        itertools.chain.from_iterable(
            itertools.starmap(
                load_file,
                zip(files, itertools.repeat(resolution), itertools.repeat(False)),
            )
        )
    )

    if not len(obj):
        raise FileNotFoundError("Directory seems to be empty.")

    return obj


def repl(locals: Mapping[str, Any] | None = None, filename: str = "<console>") -> None:
    """# `tdbear.analyzer.repl()`

    Starts an interactive Python session.

    ## Args
    - `locals`   : Default namespace.
    - `filename` : File name of the input stream.

    ## Examples
    ```python
    import tdbear.analyzer as ta

    ta.repl(locals())
    ```
    """

    import code

    code.InteractiveConsole(locals, filename).interact()


def show(*args, **kwargs):
    """# `tdbear.analyzer.show()`

    Displays all open figures. Argument types
    are the same as that of `matplotlib.pyplot.show()`.

    ## Examples
    ```python
    import tdbear.analyzer as ta

    dataset = ta.load_dir("./nanakoberry/**/")
    dataset.merge().draw(show=False)

    ta.show()
    ```
    """

    return plt.show(*args, **kwargs)
