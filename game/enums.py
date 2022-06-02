"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

from enum import Enum


class GameStates(Enum):
    MAIN_MENU = "main menu"
    LEVEL = "level"
    DEATH_SCREEN = "death screen"
