"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import math

import esper
import pygame
import logging

from game.components import (CollisionTile, Frames, Movement,
                             PlayerData, Pos, Rectangle, Sword, Tile)
from game.generics import EventInfo
from game.utils import get_movement


logger = logging.getLogger()


class InputProcessor(esper.Processor):
    def process(self, event_info: EventInfo):
        dt = event_info["dt"]
        keys = event_info["keys"]
        mouse_pos = event_info["mouse pos"]

        clicked = False
        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        for entity, (
            pos,
            movement,
            player_data,
            sword,
        ) in self.world.get_components(Pos, Movement, PlayerData, Sword):
            movement.x, movement.y = 0, 0
            if keys[pygame.K_w]:
                movement.y -= player_data.speed * dt
            if keys[pygame.K_s]:
                movement.y += player_data.speed * dt
            if keys[pygame.K_d]:
                movement.x += player_data.speed * dt
            if keys[pygame.K_a]:
                movement.x -= player_data.speed * dt

            if clicked:
                sword.piercing = True

            if not sword.piercing:
                sword.pos = pos.copy()

            angle = math.degrees(
                math.atan2(
                    mouse_pos[1] - sword.pos.y,
                    mouse_pos[0] - sword.pos.x,
                )
            )
            sword.image = pygame.transform.rotate(sword.original_image, -angle)

            if sword.piercing:
                if sword.distance < sword.MAX_DISTANCE:
                    dx, dy = get_movement(angle, sword.PIERCING_SPEED)
                    sword.pos.x += dx * dt
                    sword.pos.y += dy * dt

                    sword.distance += math.sqrt(
                        ((dx * dt) ** 2) + ((dy * dt) ** 2)
                    )
                else:
                    sword.piercing = False
                    sword.distance = 0

            sword.rect.midbottom = sword.pos


class CollisionProcessor(esper.Processor):
    def process(self, event_info: EventInfo):
        for entity, (pos, movement, rect) in self.world.get_components(
            Pos, Movement, Rectangle
        ):
            for tile_entity, (tile, *_) in self.world.get_components(
                CollisionTile
            ):
                if tile.rect.colliderect(
                    pygame.Rect(rect.x + movement.x, rect.y, *rect.size)
                ):
                    movement.x = 0
                if tile.rect.colliderect(
                    pygame.Rect(rect.x, rect.y + movement.y, *rect.size)
                ):
                    movement.y = 0

            rect.midbottom = pos + movement


class MovementProcessor(esper.Processor):
    def process(self, event_info: EventInfo):
        for entity, (pos, movement) in self.world.get_components(Pos, Movement):
            pos += movement


class RenderProcessor(esper.Processor):
    def process(self, event_info: EventInfo):
        screen = event_info["screen"]
        dt = event_info["dt"]
        for entity, (tile, *_) in self.world.get_components(Tile):
            screen.blit(tile.image, tile.pos)

        for entity, (tile, *_) in self.world.get_components(CollisionTile):
            screen.blit(tile.image, tile.rect)

        for entity, (frames, pos, rect) in self.world.get_components(
            Frames, Pos, Rectangle
        ):
            frames.animation.update(dt)
            frames.animation.draw(screen, pos, blit_by="midbottom")

        for entity, (sword, *_) in self.world.get_components(Sword):
            screen.blit(sword.image, sword.rect)
