from __future__ import annotations


class Console:
    RESET = 0
    BOLD = 1
    UNDERLINE = 4
    REVERCE = 7
    INVISIBLE = 8
    BLACK = 30
    RED = 31
    GREEN = 32
    YELLOW = 33
    BLUE = 34
    MAGENTA = 35
    CYAN = 36
    WHITE = 37
    COLOR_DEFAULT = 39
    BG_BLACK = 40
    BG_RED = 41
    BG_GREEN = 42
    BG_YELLOW = 43
    BG_BLUE = 44
    BG_MAGENTA = 45
    BG_CYAN = 46
    BG_WHITE = 47
    BG_DEFAULT = 49

    @staticmethod
    def strcolor(string: str, color: int, bg: int, /) -> str:
        return f"\033[{color}m\033[{bg}m{string}\033[0m"

    @classmethod
    def printc(
        cls, *args: str | tuple[str, int] | tuple[str, int, int], end: str = "\n"
    ) -> None:
        for elem in args:
            if isinstance(elem, tuple):
                if len(elem) == 2:
                    print(cls.strcolor(*elem, 49), end="")
                else:
                    print(cls.strcolor(*elem), end="")
            else:
                print(elem, end="")

        print("", end=end)

    @classmethod
    def log(cls, *args: str | tuple[str, int] | tuple[str, int, int]) -> None:
        cls.printc("> ", *args)

    @staticmethod
    def clearRow() -> None:
        print("\033[2K", end="")
