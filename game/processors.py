"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import logging
import math
import random

import esper
import pygame

from game.components import (CollisionTile, Frames, Movement, PlayerData, Pos,
                             Rectangle, Skeleton, SkeletonSpawnerTile, Sword,
                             Tile)
from game.generics import Assets, EventInfo, Vec
from game.utils import get_movement
from game.utils.animation import Animation
from game.utils.classes import Time

logger = logging.getLogger()


class EntityProcessor(esper.Processor):
    def __init__(self, assets: Assets):
        self.assets = assets
        self.skeleton_gen_count = random.randrange(2, 6)

    def spawn_skeletons(self, event_info: EventInfo):
        for entity, (tile, *_) in self.world.get_components(
            SkeletonSpawnerTile
        ):
            if tile.gen_timer.update():
                for _ in range(self.skeleton_gen_count):
                    frames_component = Frames(
                        Animation(self.assets["skeleton"][:2], speed=0.03),
                        blit_by="topleft",
                    )
                    skeleton_rect = Rectangle(
                        self.assets["skeleton"][0].get_bounding_rect()
                    )
                    skeleton = Skeleton(50, random.uniform(0.3, 0.5))
                    self.world.create_entity(
                        skeleton,
                        frames_component,
                        Pos(tile.pos),
                        skeleton_rect,
                        Movement(0, 0)
                    )
                    self.skeleton_gen_count = random.randrange(2, 6)

    def process(self, event_info: EventInfo):
        self.spawn_skeletons(event_info)


class InputProcessor(esper.Processor):
    SMOOTH_DIAGONAL = math.sqrt(2) / 2

    def __init__(self):
        self.player_pos = (70, 50)

    def player_input_handler(self, clicked, event_info):
        dt = event_info["dt"]
        keys = event_info["keys"]
        mouse_pos = event_info["mouse pos"]
        for entity, (
            pos,
            movement,
            player_data,
            sword,
        ) in self.world.get_components(Pos, Movement, PlayerData, Sword):
            self.player_pos = pos
            movement.x, movement.y = 0, 0
            if keys[pygame.K_w]:
                movement.y -= player_data.speed * dt
            if keys[pygame.K_s]:
                movement.y += player_data.speed * dt
            if keys[pygame.K_d]:
                movement.x += player_data.speed * dt
            if keys[pygame.K_a]:
                movement.x -= player_data.speed * dt

            if movement.x and movement.y:
                movement.x *= self.SMOOTH_DIAGONAL
                movement.y *= self.SMOOTH_DIAGONAL

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

    def skeleton_input_handler(self, dt):
        for entity, (skeleton, movement) in self.world.get_components(Skeleton, Movement):
            movement.x, movement.y = 0, 0
            movement.move_towards(
                self.player_pos, skeleton.speed * dt
            )

    def process(self, event_info: EventInfo):
        dt = event_info["dt"]
        keys = event_info["keys"]
        mouse_pos = event_info["mouse pos"]

        clicked = False
        for event in event_info["events"]:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        self.player_input_handler(clicked, event_info)
        self.skeleton_input_handler(dt)


class CollisionProcessor(esper.Processor):
    def tile_collision_handler(self):
        for entity, (pos, movement, rect, frames) in self.world.get_components(
            Pos, Movement, Rectangle, Frames
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

            setattr(rect, frames.blit_by, pos + movement)

    def process(self, event_info: EventInfo):
        self.tile_collision_handler()


class MovementProcessor(esper.Processor):
    def process(self, event_info: EventInfo):
        for entity, (pos, movement) in self.world.get_components(
            Pos, Movement
        ):
            pos += movement


class RenderProcessor(esper.Processor):
    def process(self, event_info: EventInfo):
        screen = event_info["screen"]
        dt = event_info["dt"]
        for entity, (tile, *_) in self.world.get_components(Tile):
            screen.blit(tile.image, tile.pos)

        for entity, (frames, pos) in self.world.get_components(Frames, Pos):
            frames.animation.update(dt)
            frames.animation.draw(screen, pos, blit_by=frames.blit_by)

        for entity, (sword, *_) in self.world.get_components(Sword):
            screen.blit(sword.image, sword.rect)
