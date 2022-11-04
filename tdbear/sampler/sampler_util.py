from __future__ import annotations
from typing import Iterable, Sequence, Any
import random
import os
import yaml
from .._util import Console


# UTIL FUNTCIONS
# make new directory if not exist
def new_dir(dirPath: str) -> None:
    if not os.path.exists(dirPath):
        try:
            os.makedirs(dirPath)
            Console.log((f'"{dirPath}"', Console.YELLOW), (" was created successfully"))
        except Exception as e:
            Console.printc((str(e), Console.RED, Console.BG_WHITE))


# make new file if not exist
def new_file(filePath: str, content: str) -> None:
    if not os.path.isfile(filePath):
        try:
            with open(filePath, mode="w", encoding="UTF-8", newline="\n") as f:
                f.write(content)
                Console.log(
                    (f'"{filePath}"', Console.YELLOW), " was created successfully"
                )
        except Exception as e:
            Console.printc((str(e), Console.RED, Console.BG_WHITE))


# init TDS task record
def init_record(buttons: Sequence[str]) -> dict[str, dict[str, list]]:
    return {"meta": {}, "data": {elem: [] for elem in buttons}}


# dict object to csv string
def dict2yaml(
    dic: dict[str, dict[str, list]],
    duration: float,
    comments: str | Iterable[str] | None = None,
) -> str:

    result = ""

    if comments is None:
        pass
    elif isinstance(comments, str):
        result += "# " + comments + "\n\n"
    else:
        result += "\n".join(map(lambda s: "# " + str(s), comments)) + "\n\n"

    result += yaml.dump({**dic, "duration": duration})

    return result


# create button labels from attribute.txt format string
def attributetxt2list(attrs: Iterable[str], shuffle: bool) -> list[str]:
    symbols = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"

    # attribute words list
    if isinstance(attrs, str):
        attrs = attrs.replace("\r", "\n").replace("\t", " ").split("\n")

    # remove comments
    attrs = map(lambda x: str.strip(x.split(":")[0]), dict.fromkeys(attrs))

    # remove empty lines and symbols
    attrs = filter(lambda e: len(e) and e[0] not in symbols, attrs)

    # remove duplicate attributes
    attrs = [*dict.fromkeys(attrs)]

    if shuffle:
        random.shuffle(attrs)

    return attrs


# make list[str] from list[Any] or Any
def to_strlist(arr: Any) -> list[str]:
    if isinstance(arr, list):
        if not len(arr):
            return ["unknown"]
        else:
            return list(map(str, arr))
    else:
        return [str(arr)]
