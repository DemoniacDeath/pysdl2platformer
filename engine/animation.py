from __future__ import annotations

from typing import List

import sdl2

from engine.render import RenderObject


class Animation(object):
    frames: List[RenderObject]
    startTick: int
    speed: int
    turnedLeft: bool

    def __init__(self, speed: int) -> None:
        self.frames = list()
        self.startTick = sdl2.SDL_GetTicks()
        self.speed = speed
        self.turnedLeft = False

    @classmethod
    def animation_with_single_render_object(cls, render_object: RenderObject) -> Animation:
        animation = Animation(1)
        animation.add_frame(render_object)
        return animation

    @classmethod
    def animation_with_speed_and_texture_path(
            cls,
            speed: int,
            renderer:
            sdl2.SDL_Renderer,
            file_path: bytes,
            width: int,
            height: int,
            frames: int
    ) -> Animation:
        animation = Animation(speed)
        rect = sdl2.SDL_Rect()
        rect.w = width
        rect.h = height
        rect.x = rect.y = 0
        render_object = RenderObject.render_object_from_file_with_frame(renderer, file_path, rect.__copy__())
        animation.add_frame(render_object)
        for i in range(1, frames):
            rect.y = i * rect.h
            new_render_object = RenderObject(render_object.texture)
            new_render_object.fullRender = render_object.fullRender
            new_render_object.renderFlip = render_object.renderFlip
            new_render_object.renderFrameSize = rect.__copy__()
            animation.add_frame(new_render_object)
        return animation

    def add_frame(self, frame: RenderObject) -> None:
        self.frames.append(frame)

    def turn_left(self, to_the_left: bool) -> None:
        if to_the_left and not self.turnedLeft:
            flip = sdl2.SDL_FLIP_HORIZONTAL
            self.turnedLeft = True
        elif not to_the_left and self.turnedLeft:
            flip = sdl2.SDL_FLIP_NONE
            self.turnedLeft = False
        else:
            return

        for frame in self.frames:
            frame.renderFlip = flip

    def animate(self) -> RenderObject:
        ticks = sdl2.SDL_GetTicks()
        if ticks - self.startTick >= len(self.frames) * self.speed:
            self.startTick = ticks
        return self.frames[int((ticks - self.startTick) / self.speed)]
