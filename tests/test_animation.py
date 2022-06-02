"""
This file is a part of the 'ecs-pygame' source code.
The source code is distributed under the MIT license.
"""

import pygame

from game import Animation, get_images

screen = pygame.display.set_mode((420, 250), pygame.SCALED)
clock = pygame.time.Clock()
FPS_CAP = 120

surf = pygame.image.load("assets/sprites/player.png").convert_alpha()
test_frames = get_images(surf, 1, 3, 16, bound=True)
test_animation = Animation(test_frames, speed=0.05)

dt, raw_dt = 0, 0
while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            raise SystemExit

    screen.fill("black")
    test_animation.update(dt)
    test_animation.draw(screen, (50, 50), blit_by="midbottom")

    pygame.display.flip()
    raw_dt = min(clock.tick(FPS_CAP) / 1000, 0.3)
    dt = raw_dt * FPS_CAP
