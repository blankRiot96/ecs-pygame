"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import json
import logging

import esper
import pygame

from game.components import Frames, Movement, PlayerData, Pos, Rectangle, Sword
from game.enums import GameStates
from game.generics import EventInfo
from game.processors import (CollisionProcessor, MovementProcessor,
                             RenderProcessor)
from game.states import Level
from game.utils.animation import Animation
from game.utils.maps import load_map
from game.utils.sprites import load_assets

logger = logging.getLogger()


class Game:
    """
    A class that handles all events within the game.
    """

    CAP_FPS = 120
    DISPLAY_RES = (416, 336)
    TILE_SIZE = 16

    def __init__(self):
        self.logging_config()

        self.world = esper.World()
        self.screen = pygame.display.set_mode(self.DISPLAY_RES, pygame.SCALED)
        pygame.init()
        self.state = GameStates.LEVEL
        self.assets = load_assets(self.state.value, self.screen)

        with open("assets/data/level_0.json") as f:
            level_map = json.load(f)
        load_map(
            self.world, level_map, self.assets["tile_set"], self.TILE_SIZE
        )
        self.selective_load()

        self.clock = pygame.time.Clock()

    def logging_config(self):
        logging.basicConfig()
        logger.setLevel("INFO")

    def selective_load(self):
        """
        Load instances of entities, components and processors
        based on the game state.
        """

        if self.state == GameStates.MAIN_MENU:
            pass
        elif self.state == GameStates.LEVEL:
            self.player = self.world.create_entity(
                Pos(70, 50),
                Movement(),
                Rectangle((70, 50), self.assets["player"][0].get_size()),
                PlayerData(speed=0.7),
                Frames(
                    Animation(self.assets["player"], speed=0.05), self.screen
                ),
                Sword(
                    image=self.assets["sword"].copy(),
                    pos=Pos(70, 50),
                ),
            )
            self.movement_processor = MovementProcessor()
            self.collision_processor = CollisionProcessor()
            self.render_processor = RenderProcessor()
            self.world.add_processor(self.movement_processor, priority=2)
            self.world.add_processor(self.collision_processor, priority=1)
            self.world.add_processor(self.render_processor)

            self.current_state = Level(self.world, self.player)
        elif self.state == GameStates.DEATH_SCREEN:
            pass
        else:
            raise ValueError(f"No such state '{self.state}' exists!")

    def selective_process(self, event_info: EventInfo):
        if self.state == GameStates.LEVEL:
            self.current_state.update(event_info["dt"])
            self.movement_processor.process(event_info)
            self.collision_processor.process()
            self.render_processor.process(self.screen, event_info["dt"])

    def process(self):

        dt, raw_dt = 0, 0
        while True:
            events = pygame.event.get()
            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            event_info = {
                "dt": dt,
                "raw dt": raw_dt,
                "keys": keys,
                "mouse pos": mouse_pos,
                "events": events,
            }
            for event in events:
                if event.type == pygame.QUIT:
                    raise SystemExit

            self.screen.fill((25, 25, 25))

            self.selective_process(event_info)

            raw_dt = self.clock.tick(self.CAP_FPS) / 1000
            dt = raw_dt * self.CAP_FPS
            pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.process()
