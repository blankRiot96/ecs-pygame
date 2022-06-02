"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

from dataclasses import dataclass as component

import pygame

from game.generics import Vec
from game.utils.animation import Animation
from game.utils.classes import Time


class Rectangle(pygame.Rect):
    pass


class Movement(Vec):
    pass


class Pos(Vec):
    pass


@component
class Frames:
    animation: Animation
    blit_by: str


@component
class Skeleton:
    hp: int
    speed: float


@component
class PlayerData:
    speed: float


class Sword:
    MAX_DISTANCE = 50
    PIERCING_SPEED = 2.5

    def __init__(self, image: pygame.Surface, pos: Pos):
        self.image = image.copy()
        self.original_image = image.copy()
        self.pos = pos
        self.rect = image.get_bounding_rect()
        self.rect.midbottom = pos
        self.distance = 0
        self.piercing = False
        self.angle = 0


@component
class Tile:
    image: pygame.Surface
    pos: tuple


@component
class CollisionTile:
    image: pygame.Surface
    rect: pygame.Rect


class SkeletonSpawnerTile:
    SKELETON_GEN_TIME = 8.3

    def __init__(self, image: pygame.Surface, pos: tuple):
        self.image = image
        self.pos = pos
        self.gen_timer = Time(self.SKELETON_GEN_TIME)
