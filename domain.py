from __future__ import annotations
import numpy as np
from typing import NamedTuple
from enum import Enum
from dataclasses import dataclass

class Size(NamedTuple):
    width: int
    height: int


class Color(NamedTuple):
    red: int
    green: int
    blue: int

    @property
    def rgb(self) -> tuple[int, int, int]:
        return (self.red, self.green, self.blue)
    
    @property
    def bgr(self) -> tuple[int, int, int]:
        return (self.blue, self.green, self.red)
    

Color.BLACK = Color(0, 0, 0)
Color.WHITE = Color(255, 255, 255)
Color.BLUE = Color(0, 0, 255)
Color.GREEN = Color(0, 255, 0)
Color.RED = Color(255, 0, 0)
Color.DARK_RED = Color(204, 40, 47)
Color.LIGHT_RED = Color(236, 194, 198)
Color.YELLOW = Color(255, 255, 0)
Color.MAGENTA = Color(255, 0, 255)
Color.CYAN = Color(0, 255, 255)
Color.PLATINUM = Color(229, 228, 226)
Color.SILVER = Color(192, 192, 192)
Color.DARK_GRAY = Color(169, 169, 169)
Color.SAGE_GREEN = Color(138, 154, 91)
Color.CHARCOAL = Color(54, 69, 79)
Color.BRONZE = Color(205, 127, 50)
Color.TEAL = Color(0, 128, 128)
Color.GOLD = Color(255,215,0)
Color.YELLOW_GREEN = Color(154,205,50)
Color.FOREST_GREEN = Color(34,139,34)
Color.BLUE_VIOLET = Color(138,43,226)
Color.ORCHID = Color(218,112,214)
Color.SADDLE_BROWN = Color(139,69,19)


def color_combintation(first: Color, coeff: float, second: Color) -> Color:
    first_arr = np.array(first, dtype=np.int16)
    second_arr = np.array(second, dtype=np.int16)
    result_arr = first_arr * coeff + second_arr * (1 - coeff)
    return Color(*result_arr)

def color_gradient(min_color: Color, middle_color: Color, max_color: Color, min_value: float, max_value: float, value: float):
    ratio = 2 * ((value - min_value) / (max_value - min_value)) - 1
    if ratio < -1:
        ratio = -1
    if ratio > 1:
        ratio = 1
    min_color_arr = np.array(min_color, dtype=np.float32)
    max_color_arr = np.array(max_color, dtype=np.float32)
    middle_color_arr = np.array(middle_color, dtype=np.float32)
    if ratio <= 0:
        result_arr = middle_color_arr + abs(ratio) * (min_color_arr - middle_color_arr)
    else:
        result_arr = middle_color_arr + abs(ratio) * (max_color_arr - middle_color_arr) 
    return Color(int(result_arr[0]), int(result_arr[1]), int(result_arr[2]))


class Position(NamedTuple):
    x: int
    y: int

    def shift_x(self, value: int) -> Position:
        return Position(self.x + value, self.y)
    
    def shift_y(self, value: int) -> Position:
        return Position(self.x, self.y + value)

    def __add__(self, other) -> Position:
        return Position(self.x + other.x, self.y + other.y)

    def __sub__(self, other) -> Position:
        return Position(self.x - other.x, self.y - other.y)
    
    def __mul__(self, value: float) -> Position:
        return Position(int(self.x * value), int(self.y * value))

    def __rmul__(self, value: float) -> Position:
        return Position(int(self.x * value), int(self.y * value))
    
    def __truediv__(self, value: float) -> Position:
        return Position(int(self.x / value), int(self.y / value))


class Orientation(Enum):
    START = 0
    MIDDLE = 1
    END = 2


@dataclass(frozen=True)
class PositionOrientation:
    x: Orientation
    y: Orientation


PositionOrientation.TOP_LEFT = PositionOrientation(Orientation.START, Orientation.START)
PositionOrientation.TOP_RIGHT = PositionOrientation(Orientation.END, Orientation.START)
PositionOrientation.BOTTOM_LEFT = PositionOrientation(Orientation.START, Orientation.END)
PositionOrientation.BOTTOM_RIGHT = PositionOrientation(Orientation.END, Orientation.END)
PositionOrientation.MIDDLE_LEFT = PositionOrientation(Orientation.START, Orientation.MIDDLE)
PositionOrientation.MIDDLE_RIGHT = PositionOrientation(Orientation.END, Orientation.MIDDLE)
PositionOrientation.TOP_MIDDLE = PositionOrientation(Orientation.MIDDLE, Orientation.START)
PositionOrientation.BOTTOM_MIDDLE = PositionOrientation(Orientation.MIDDLE, Orientation.END)
PositionOrientation.MIDDLE_MIDDLE = PositionOrientation(Orientation.MIDDLE, Orientation.MIDDLE)


def orient_pos(pos: Position, size: Size, ort_from: PositionOrientation, ort_to: PositionOrientation) -> Position:
    # To top left
    match ort_from.x:
        case Orientation.MIDDLE:
            pos = pos.shift_x(-size.width // 2)
        case Orientation.END:
            pos = pos.shift_x(-size.width)
    match ort_from.y:
        case Orientation.MIDDLE:
            pos = pos.shift_y(-size.height // 2)
        case Orientation.END:
            pos = pos.shift_y(-size.height)
    # From top let
    match ort_to.x:
        case Orientation.MIDDLE:
            pos = pos.shift_x(size.width // 2)
        case Orientation.END:
            pos = pos.shift_x(size.width)
    match ort_to.y:
        case Orientation.MIDDLE:
            pos = pos.shift_y(size.height // 2)
        case Orientation.END:
            pos = pos.shift_y(size.height)
    return pos


class Rectangle(NamedTuple):
    left: int
    top: int
    width: int
    height: int

    def get_oriented_pos(self, ort: PositionOrientation):
        return orient_pos(self.top_left_pos, self.size, PositionOrientation.TOP_LEFT, ort)

    @property
    def top_left_pos(self) -> Position:
        return Position(self.left, self.top)
    
    @property
    def top_middle_pos(self) -> Position:
        return self.get_oriented_pos(PositionOrientation.TOP_LEFT)
    
    @property
    def top_right_pos(self) -> Position:
        return self.get_oriented_pos(PositionOrientation.TOP_RIGHT)

    @property
    def bottom_left_pos(self) -> Position:
        return self.get_oriented_pos(PositionOrientation.BOTTOM_LEFT)
    
    @property
    def bottom_right_pos(self) -> Position:
        return self.get_oriented_pos(PositionOrientation.BOTTOM_RIGHT)
    
    @property
    def middle_right_pos(self) -> Position:
        return self.get_oriented_pos(PositionOrientation.MIDDLE_RIGHT)

    @property
    def size(self) -> Size:
        return Size(self.width, self.height)

    @staticmethod
    def from_pos_size(pos: Position, size: Size) -> Rectangle:
        return Rectangle(pos.x, pos.y, size.width, size.height)
    
    @staticmethod
    def from_pos_size_ort(pos: Position, size: Size, ort: PositionOrientation) -> Rectangle:
        return Rectangle.from_pos_size(orient_pos(pos, size, ort, PositionOrientation.TOP_LEFT), size)
    
class Dipole:
    def __init__(self, pos: np.array = np.array([0, 0]), actangle: float=0, c_vel: np.array = np.array([0, 0]).astype(float), w: float = 0):
        self.pos = pos
        self.actangle = actangle
        self.c_vel = c_vel
        self.w = w