"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import esper
import pygame

from game.components import CollisionTile, Tile, SkeletonSpawnerTile
from game.generics import Assets


def load_map(
    world: esper.World, level_map: list[str], tile_set, tile_size: int
):
    tile_images = {".": tile_set[0], "x": tile_set[1], "s": tile_set[2]}
    for row_number, row in enumerate(level_map):
        for col_number, col in enumerate(row.split(" ")[:-1]):
            image = tile_images[col]
            rect = pygame.Rect(
                (col_number * tile_size, row_number * tile_size),
                (tile_size, tile_size),
            )
            if col == ".":
                tile = Tile(image, rect.topleft)
            elif col == "x":
                tile = CollisionTile(rect)
                world.create_entity(tile, Tile(image, rect.topleft))
                continue
            elif col == "s":
                tile = SkeletonSpawnerTile(image, rect.topleft)
                world.create_entity(tile, Tile(image, rect.topleft))
                continue
            world.create_entity(tile)
