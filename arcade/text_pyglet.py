"""
Drawing text with pyglet label
"""
import math
from typing import Tuple, Union

import arcade
import pyglet
from arcade.arcade_types import Color
from arcade.draw_commands import get_four_byte_color
from pyglet.math import Mat4
from arcade.resources import resolve_resource_path


def load_font(font_name):
    """ Load a font for later use """
    if font_name.startswith(":resources:"):
        try:
            file_path = resolve_resource_path(font_name)
        except FileNotFoundError:
            raise FileNotFoundError(f"Unable to find resource with the name: {font_name}")
    else:
        file_path = font_name

    pyglet.font.add_file(str(file_path))


FontNameOrNames = Union[str, Tuple[str, ...]]


def attempt_font_name_resolution(font_name: FontNameOrNames) -> FontNameOrNames:
    """
    Attempt to resolve a tuple of font names.

    Preserves the original logic of this section, even though it
    doesn't seem to make sense entirely. Comments are an attempt
    to make sense of the original code.

    If it can't resolve a definite path, it will return the original
    argument for pyglet to attempt to resolve. This is consistent with
    the original behavior of this code before it was encapsulated.

    :param Union[str, Tuple[str, ...]] font_name:
    :return: Either a resolved path or the original tuple
    """
    if font_name:

        # ensure
        if isinstance(font_name, str):
            font_list: Tuple[str, ...] = (font_name,)
        elif isinstance(font_name, tuple):
            font_list = font_name
        else:
            raise TypeError("font_name parameter must be a string, or a tuple of strings that specify a font name.")

        for font in font_list:
            try:
                path = resolve_resource_path(font)
                # print(f"Font path: {path=}")

                # found a font successfully!
                return path.name

            except FileNotFoundError:
                pass

    # failed to find it ourselves, hope pyglet can make sense of it
    return font_name


def _draw_label_with_rotation(label: pyglet.text.Label, rotation: float) -> None:
    """

    Helper for drawing pyglet labels with rotation within arcade.

    Originally part of draw_text in this module, now abstracted and improved
    so that both arcade.Text and arcade.draw_text can make use of it.

    :param pyglet.text.Label label: a pyglet label to wrap and draw
    :param float rotation: rotate this many degrees from horizontal around anchor
    :return:
    """

    # raw pyglet draw functions need this context helper inside arcade
    window = arcade.get_window()
    with window.ctx.pyglet_rendering():

        # execute view matrix magic to rotate cleanly
        if rotation:
            # original_view = window.view

            angle_radians = math.radians(rotation)
            x = label.x
            y = label.y
            label.x = 0
            label.y = 0
            rview = Mat4().rotate(angle_radians, x=0, y=0, z=1)
            tview = Mat4().translate(x=x, y=y, z=0)
            final_view = rview @ tview
            window.view = final_view

        label.draw()

        # restore original position if we used view matrix magic
        if rotation:
            # linters might warn that this is used before assignment,
            # but it's actually valid since we only use it when it was
            # previously assigned.
            label.x, label.y = x, y


class Text:

    def __init__(
        self,
        text: str,
        start_x: float,
        start_y: float,
        color: Color = arcade.color.WHITE,
        font_size: float = 12,
        width: int = 0,
        align: str = "left",
        font_name: FontNameOrNames = ("calibri", "arial"),
        bold: bool = False,
        italic: bool = False,
        anchor_x: str = "left",
        anchor_y: str = "baseline",
        multiline: bool = False,
        rotation: float = 0
    ):

        if align != "center" and align != "left" and align != "right":
            raise ValueError("The 'align' parameter must be equal to 'left', 'right', or 'center'.")

        if align != "left":
            multiline = True

        adjusted_font = attempt_font_name_resolution(font_name)
        self._label = pyglet.text.Label(
            text=text,
            x=start_x,
            y=start_y,
            font_name=adjusted_font,
            font_size=font_size,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=get_four_byte_color(color),
            width=width,
            align=align,
            bold=bold,
            italic=italic,
            multiline=multiline
        )
        self.rotation = rotation

    @property
    def value(self) -> str:
        return self._label.text

    @value.setter
    def value(self, value: str):
        self._label.text = value

    def draw(self):
        _draw_label_with_rotation(self._label, self.rotation)


def draw_text(
    text: str,
    start_x: float,
    start_y: float,
    color: Color = arcade.color.WHITE,
    font_size: float = 12,
    width: int = 0,
    align: str = "left",
    font_name: FontNameOrNames = ("calibri", "arial"),
    bold: bool = False,
    italic: bool = False,
    anchor_x: str = "left",
    anchor_y: str = "baseline",
    multiline: bool = False,
    rotation: float = 0,
):
    """
    Draws text to the screen using Pyglet's label instead.

    :param str text: Text to draw
    :param float start_x:
    :param float start_y:
    :param Color color: Color of the text
    :param float font_size: Size of the text
    :param float width:
    :param str align:
    :param Union[str, Tuple[str, ...]] font_name:
    :param bool bold:
    :param bool italic:
    :param str anchor_x:
    :param str anchor_y:
    :param bool multiline:
    :param bool wrap_lines:
    :param float rotation:
    """
    # See : https://github.com/pyglet/pyglet/blob/ff30eadc2942553c9de96d6ce564ad1bc3128fb4/pyglet/text/__init__.py#L401

    color = get_four_byte_color(color)
    # Cache the states that are expensive to change
    key = f"{font_size}{font_name}{bold}{italic}{anchor_x}{anchor_y}{align}{width}"
    cache = arcade.get_window().ctx.pyglet_label_cache
    label = cache.get(key)
    if align != "center" and align != "left" and align != "right":
        raise ValueError("The 'align' parameter must be equal to 'left', 'right', or 'center'.")
    if align != "left":
        multiline = True

    if not label:
        adjusted_font = attempt_font_name_resolution(font_name)

        label = pyglet.text.Label(
            text=text,
            x=start_x,
            y=start_y,
            font_name=adjusted_font,
            font_size=font_size,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
            color=color,
            width=width,
            align=align,
            bold=bold,
            italic=italic,
            multiline=multiline,
        )
        cache[key] = label

    # These updates are relatively cheap
    label.text = text
    label.x = start_x
    label.y = start_y
    label.color = color

    _draw_label_with_rotation(label, rotation)


# TODO: maybe remove, as this is invalid
def create_text(*args, **kwargs):
    return Text("Hello")
