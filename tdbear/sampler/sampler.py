from __future__ import annotations
from typing import Callable, Iterable, Any
import time
import os
import datetime

import PySimpleGUI as sg

from .._util import Console
from .sampler_options import Options
from . import sampler_util as su


# GUI FUNTCIONS
# MAIN WINDOW
def run() -> None:
    """# `tdbear.sampler.run()`"""

    # print status
    Console.log(("Constructing GUI...", Console.CYAN))

    # set PySimpleGUI theme
    sg.theme(Options.theme)

    # variables for gui components
    buttons: list[str] = []  # button labels
    buttonField: list[list] = [[]]  # button components
    maxTextLen: int = 0  # use as button size

    commonFrameArgs: dict = {"title": "", "border_width": 0}
    commonButtonArgs: dict = {
        "auto_size_button": True,
        "focus": False,
        "bind_return_key": False,
    }

    # convert parameters to list[str]
    outputFileNumber: list[str] = su.to_strlist(Options.output_file_number)

    outputFolder: list[str] = su.to_strlist(Options.output_folder)

    productName: list[str] = su.to_strlist(Options.product_name)

    # create button labels from attribute words
    if Options.attributes is None:
        # make a new txt file of atribute words if not exist
        su.new_file(Options.attribute_list_path, "SWEET\nSOUR\nBITTER\n")
        try:
            with open(Options.attribute_list_path, "r", encoding="UTF-8") as attrs:
                buttons = su.attributetxt2list(
                    attrs.read(), shuffle=Options.button_shuffle
                )

        except Exception as e:
            Console.printc((str(e), Console.RED, Console.BG_WHITE))
    else:
        buttons = su.attributetxt2list(
            Options.attributes, shuffle=Options.button_shuffle
        )

    # create button components from button labels
    for elem in buttons:
        elemWidth: int = sum(1 + (len(str.encode(char)) >= 2) for char in elem)
        lastElem: list = buttonField[-1]
        buttonSize: int = 10 + (elemWidth >= 10)
        maxTextLen: int = max(elemWidth, maxTextLen)

        lastElem.append(
            sg.Submit(
                **commonButtonArgs,
                button_text=elem,
                button_color=(Options.button_text_color, Options.button_color_disabled),
                size=(buttonSize, None),
                pad=(
                    (Options.button_padding, Options.button_padding),
                    (0, Options.button_padding * 2),
                ),
            )
        )

        if len(lastElem) == Options.max_column:
            buttonField.append([])

    # gui components
    startButton: list[list] = [
        [
            sg.Submit(
                **commonButtonArgs,
                button_text=startButtonList,
                button_color=Options.button_color_start,
                pad=(
                    (Options.button_padding, Options.button_padding),
                    (Options.button_padding, Options.button_padding * 2),
                ),
            )
            for startButtonList in {" START ", " STOP ", " SAVE & RESET "}
        ]
    ]
    statusIndicator: list[list] = [
        [sg.Text(text="Not Started ⏹", text_color="#000000", key=" status ")]
    ]
    outputFolderSetting: list[list] = [
        [sg.Text("Output Folder:")],
        [
            sg.Input(
                default_text=outputFolder[0],
                size=(10, 1),
                border_width=2,
                key=" folder ",
            )
        ],
    ]
    outputFileSetting: list[list] = [
        [sg.Text("Output File:")],
        [
            sg.Input(
                default_text=str(Options.output_file_prefix),
                size=(10, 1),
                border_width=2,
                key=" output ",
            ),
            sg.Text(Options.output_file_joint),
            sg.Input(
                default_text=outputFileNumber[0],
                size=(5, 1),
                border_width=2,
                key=" filenumber ",
            )
            if Options.output_file_number is not None
            else sg.Text(),
            sg.Text(f"{Options.output_file_suffix}" f"{Options.output_file_extension}"),
        ],
    ]

    # gui layout
    layout: list[list] = [
        [
            sg.Text(
                text="TDsampler", font=(Options.font_family, Options.title_font_size)
            ),
            sg.Frame(
                **commonFrameArgs,
                element_justification="right",
                layout=statusIndicator,
                key=" statusfield ",
            ),
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Frame(
                **commonFrameArgs,
                element_justification="left",
                layout=startButton,
                key=" startbutton ",
            ),
            sg.Text(text="", size=(maxTextLen + 7, None), key=" event "),
        ],
        [
            sg.Frame(
                **commonFrameArgs,
                element_justification=Options.button_justification,
                layout=buttonField,
                key=" buttonfield ",
            )
        ],
        [sg.HorizontalSeparator()],
        [
            sg.Frame(
                **commonFrameArgs,
                element_justification="left",
                layout=outputFolderSetting,
                key=" outputfoldersetting ",
            ),
            sg.VerticalSeparator(),
            sg.Frame(
                **commonFrameArgs,
                element_justification="left",
                layout=outputFileSetting,
                key=" outputfilesetting ",
            ),
        ],
    ]

    # window component
    window = sg.Window(
        title="TDsampler",
        layout=layout,
        resizable=True,
        finalize=True,
        return_keyboard_events=True,
        font=(Options.font_family, Options.font_size),
    )

    # function that updates the gui components
    def updateWindow(keys: str | Iterable, *args, **kwargs) -> Callable:
        if isinstance(keys, str):
            keys = {keys}
        for key in keys:
            window[key].update(*args, **kwargs)

        return updateWindow

    # expand components to full width
    for key in {" statusfield ", " buttonfield "}:
        window[key].expand(expand_x=True)

    # hide the stop button and the save & reset button
    updateWindow({" SAVE & RESET ", " STOP "}, visible=False)

    # variables used in loop
    currentEvent: str = ""  # current event
    event: str = ""  # event
    values: dict[Any, Any] = {}  # values of gui components
    startTime: float = 0.0  # time when the start button is pressed

    # time (seconds) from when the the start button
    # is pressed to when the last button is pressed
    duration: float = 0.0

    # time (seconds) from when the the start button
    # is pressed to when the another button is pressed
    lapTime: float = 0.0

    # status of this application
    status: str = "initial"

    # dict object that contains time info for each attribute
    record: dict[str, dict[str, list]] = su.init_record(buttons)

    # print status
    Console.log(("Ready!\n", Console.GREEN))

    # start loop
    while True:
        # receive events and values of gui components
        events = window.read(timeout=10, timeout_key=" timeout ")

        if events is None:
            break

        [event, values] = events

        # procedures corresponding to each event
        # when event is None
        if event is None:
            if currentEvent:
                Console.log(("Your task is cancelled", Console.YELLOW))
            break

        # when the start button is pressed
        elif event == " START " and status == "initial":
            # record timing
            startTime = time.time()
            lapTime = 0.0

            # update gui components
            updateWindow(buttons, button_color=Options.button_color_off)(
                " status ", "Recording ⏺", text_color="#ff0000"
            )(" START ", visible=False)(" STOP ", visible=True)

            # print status
            Console.printc(("[START]", Console.RED))

            # update variables
            currentEvent = " START "
            status = "started"

        # when the buttons (except start) are pressed
        elif event in buttons and event != currentEvent and status == "started":

            # record timing
            lapTime = round(time.time() - startTime, 4)
            record["data"][event].append(lapTime)

            # change button color
            if currentEvent != " START ":
                updateWindow(currentEvent, button_color=Options.button_color_off)

            # update gui components
            updateWindow(event, button_color=Options.button_color_on)(
                " event ", f"NOW: {event}"
            )

            # print the pressed button
            print(event)

            # update variables
            currentEvent = event

        # when the stop button is pressed
        elif event == " STOP " and status == "started":
            # record timing
            lapTime = round(time.time() - startTime, 4)

            duration = lapTime

            # update gui components
            updateWindow(buttons, button_color=Options.button_color_disabled)(
                " status ", "Stopped ⏸", text_color="#0000ff"
            )(" STOP ", visible=False)(" SAVE & RESET ", visible=True)(" event ", "")

            # print status
            Console.printc(("[STOP]\n", Console.RED))

            # add meta info to the record
            customMeta: dict = {}
            for key in Options.custom_metadata:
                customMeta[key.strip().upper()] = Options.custom_metadata[key]

            record["meta"] |= customMeta
            record["meta"] |= {
                "ASSESSOR": [Options.assessor_name],
                "DATE": [datetime.datetime.now(datetime.timezone.utc).astimezone()],
                "PRODUCT": [productName[0]],
            }

            # record trial count (option)
            if Options.trial_count is not None:
                record["meta"] |= {"COUNT": [Options.trial_count]}

            # record score and product name (option)
            if Options.after_task_scoring:
                score = scoring_window(Options.after_task_scoring)
                record["meta"] |= {
                    "SCORE": [score],
                    "SCORE_MIN": [Options.after_task_scoring[0]],
                    "SCORE_MAX": [Options.after_task_scoring[1]],
                }

            # update valiables
            status = "stopped"

        # when the save & reset button is pressed
        elif event == " SAVE & RESET " and status == "stopped":
            # check if the file number is an integer
            fileNumber: int | str = values[" filenumber "]

            if (
                outputFileNumber is not None
                and len(outputFileNumber) == 1
                and Options.output_file_increment
            ):

                try:
                    fileNumber = int(fileNumber)
                except Exception:
                    sg.popup(
                        "File number must be an integer\n",
                        title="Error",
                        font=(Options.font_family, Options.font_size),
                    )
                    continue

            # create file name
            outputFolderPath: str = f'{values[" folder "]}/'
            outputFileName: str = (
                f'{values[" output "]}'
                f"{Options.output_file_joint}{fileNumber}"
                f"{Options.output_file_suffix}"
                f"{Options.output_file_extension}"
            )

            # confirmation before saving file
            # (notify when a file with the same name exists)
            beforeSaveConfirm: str = sg.popup_yes_no(
                f'"{outputFileName}" already exists. Overwrite it?\n'
                if os.path.isfile(f"{outputFolderPath}{outputFileName}")
                else f'Your record will be saved as "{outputFileName}". OK?\n',
                title="Confirm",
                font=(Options.font_family, Options.font_size),
            )

            # when instructed not to overwrite
            if beforeSaveConfirm != "Yes":
                continue

            # create new directory if it doesn't exist
            su.new_dir(outputFolderPath)

            # start saving
            try:
                with open(
                    f"{outputFolderPath}{outputFileName}",
                    "w",
                    encoding="UTF-8",
                    newline="\n",
                ) as outputFile:

                    outputFile.write(su.dict2yaml(record, duration, Options.comments))

            except Exception as e:
                sg.popup(
                    "Failed to save your record\n",
                    title="Error",
                    font=(Options.font_family, Options.font_size),
                )

                Console.printc((str(e), Console.RED, Console.BG_WHITE))

                continue

            print()

            # notify completion
            sg.popup(
                f'Your record has been saved in "{outputFileName}"\n',
                title="Success",
                font=(Options.font_family, Options.font_size),
            )

            # increment or change file number
            if outputFileNumber is not None and len(outputFileNumber) > 1:
                del outputFileNumber[0]
                updateWindow(" filenumber ", outputFileNumber[0])

            elif Options.output_file_increment:
                updateWindow(" filenumber ", str(int(fileNumber) + 1))

            # change folder name
            if len(outputFolder) > 1:
                del outputFolder[0]
                updateWindow(" folder ", str(outputFolder[0]))

            # change product name
            if len(productName) > 1:
                del productName[0]

            # restore gui components to initial state
            (
                updateWindow(" SAVE & RESET ", visible=False)(
                    " START ", visible=True, button_color=Options.button_color_start
                )(" status ", "Not Started ⏹", text_color="#000000")
            )

            # restore variables to initial state
            record = su.init_record(buttons)
            currentEvent = ""
            status = "initial"

    # close window if the loop is broken
    Console.log(("Bye\n", Console.CYAN))
    window.close()


# window for product rating
def scoring_window(score_range: tuple[int, int]) -> int:
    # default score
    score: int = (score_range[0] + score_range[1]) // 2

    # layout for this window
    layout: list[list] = [
        [sg.Text("Please rate this product using the slider below!")],
        [sg.HorizontalSeparator()],
        [sg.Text()],
        [
            sg.Slider(
                range=score_range,
                default_value=int(score),
                expand_x=True,
                orientation="horizontal",
                background_color=Options.button_color_off,
                text_color=Options.button_text_color,
                pad=(Options.button_padding, Options.button_padding),
                key=" score_slider ",
            )
        ],
        [sg.Text()],
        [
            sg.Submit(
                auto_size_button=True,
                focus=False,
                bind_return_key=False,
                button_text="OK",
                button_color=(Options.button_text_color, Options.button_color_off),
                size=(10, None),
                pad=(
                    (Options.button_padding, Options.button_padding),
                    (0, Options.button_padding * 2),
                ),
                key=" score_submit ",
            )
        ],
    ]

    # window component
    window = sg.Window(
        title="Scoring",
        layout=layout,
        resizable=True,
        finalize=True,
        return_keyboard_events=True,
        modal=True,
        disable_close=True,
        element_justification="center",
        font=(Options.font_family, Options.font_size),
    )

    # main loop
    while True:
        event: str
        values: dict[Any, Any]

        events = window.read(timeout=10, timeout_key=" timeout ")

        if events is None:
            break

        [event, values] = events

        # when event is None
        if event is None:
            break

        # when submitted
        if event == " score_submit ":
            score = int(values[" score_slider "])
            break

    # close window if the loop is broken
    window.close()

    return score
