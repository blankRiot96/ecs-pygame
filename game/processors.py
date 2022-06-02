"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import math

import esper
import pygame

from game.components import (CollisionTile, Frames, Image, Movement,
                             PlayerData, Pos, Rectangle, Sword, Tile)
from game.generics import EventInfo
from game.utils import get_movement


class MovementProcessor(esper.Processor):
    def __init__(self):
        self.going_towards = False 
        self.max_distance = 50
        self.distance = 0
        self.target = None 

    def process(self, event_info: EventInfo):
        dt = event_info["dt"]
        keys = event_info["keys"]
        mouse_pos = event_info["mouse pos"]

        clicked = False
        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
                self.going_towards = True

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
            if not self.going_towards:
                sword.pos = pos.copy()
            self.target = pos.copy()
            angle = (
                math.degrees(
                    math.atan2(
                        mouse_pos[1] - sword.pos.y,
                        mouse_pos[0] - sword.pos.x,
                    )
                )
            )
            sword.image = pygame.transform.rotate(sword.original_image, -angle)

            if self.going_towards:
                if self.distance < self.max_distance:
                    dx, dy = get_movement(angle, sword.pierce_speed)
                    sword.pos.x += dx * dt 
                    sword.pos.y += dy * dt

                    self.distance += math.sqrt(((dx * dt) ** 2) + ((dy * dt) ** 2))
                else:
                    self.going_towards = False
                    self.distance = 0

            sword.rect.midbottom = sword.pos


class CollisionProcessor(esper.Processor):
    def process(self):
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

            pos += movement
            rect.midbottom = pos


class RenderProcessor(esper.Processor):
    def process(self, screen: pygame.Surface, dt: float):
        for entity, (tile, *_) in self.world.get_components(Tile):
            screen.blit(tile.image, tile.pos)

        for entity, (tile, *_) in self.world.get_components(CollisionTile):
            screen.blit(tile.image, tile.rect)

        for entity, (image, pos) in self.world.get_components(Image, Pos):
            image.screen.blit(image.image, pos)

        for entity, (frames, pos, rect) in self.world.get_components(
            Frames, Pos, Rectangle
        ):
            frames.animation.update(dt)
            frames.animation.draw(frames.screen, pos, blit_by="midbottom")

        for entity, (sword, *_) in self.world.get_components(Sword):
            screen.blit(sword.image, sword.rect)
