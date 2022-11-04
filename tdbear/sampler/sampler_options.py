from __future__ import annotations
from typing import Iterable, Callable, Any


class Options:
    """# `tdbear.sampler.Options`"""

    """file path to attribute list (attribute.txt)"""
    attribute_list_path: str = "./attribute.txt"

    """instead of attribute.txt, this can be used"""
    attributes: Iterable[str] | str | None = None

    """assessor name"""
    assessor_name: str = "unknown"

    """product name(s)"""
    product_name: str | list[str] = "unknown"

    """count of trial"""
    trial_count: int | None = None

    """custom metadata"""
    custom_metadata: dict[str, Iterable] = {}

    """comments"""
    comments: str | Iterable[str] | None = None

    """attribute buttons will be shuffled if this is True"""
    button_shuffle: bool = True

    """text color of buttons"""
    button_text_color: str = "#ffffff"

    """background color of buttons (on)"""
    button_color_on: str = "#008800"

    """background color of buttons (off)"""
    button_color_off: str = "#082567"

    """background color of buttons (disabled)"""
    button_color_disabled: str = "#666666"

    """background color of start button"""
    button_color_start: str = "#bb0000"

    """background color of stop button"""
    button_color_stop: str = "#bb0000"

    """button justification (center, right, left)"""
    button_justification: str = "center"

    """button padding"""
    button_padding: int = 20

    """output folder name"""
    output_folder: str | list[str] = "output"

    """output file prefix"""
    output_file_prefix: str = "out"

    """output file joint"""
    output_file_joint: str = "-"

    """output file number"""
    output_file_number: int | str | list[str] | None = 0

    """auto increment file number if this is True"""
    output_file_increment: bool = True

    """output file suffix"""
    output_file_suffix: str = ""

    """output file extension"""
    output_file_extension: str = ".yml"

    """range of scoring"""
    after_task_scoring: tuple[int, int] | None = None

    """maximum count of button columns"""
    max_column: int = 3

    """font family for gui components"""
    font_family: str = "Meiryo UI"

    """font size for gui components"""
    font_size: int = 14

    """font size of title"""
    title_font_size: int = 25

    """PySimpleGUI theme"""
    theme: str = "SystemDefault"

    @classmethod
    def set(cls, key: str, value: Any) -> Callable:
        setattr(cls, key, value)

        return cls.set
