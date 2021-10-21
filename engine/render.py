from __future__ import annotations

import sdl2
import sdl2.sdlimage

from core.color import Color
from core.size import Size
from core.vector2d import Vector2D
from engine.context import GameContext


class RenderObject(object):
    texture: sdl2.SDL_Texture
    renderFrameSize: sdl2.SDL_Rect
    renderFlip: sdl2.SDL_RendererFlip = sdl2.SDL_FLIP_NONE
    fullRender: bool = True

    def __init__(self, texture: sdl2.SDL_Texture) -> None:
        self.texture = texture

    @classmethod
    def render_object_from_surface(cls, renderer: sdl2.SDL_Renderer, surface: sdl2.SDL_Surface) -> RenderObject:
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)
        if not texture:
            raise RuntimeError("Unable to create texture from surface! SDL Error: "
                               + str(sdl2.SDL_GetError()))
        return RenderObject(texture)

    @classmethod
    def render_object_from_color(cls, renderer: sdl2.SDL_Renderer, color: Color) -> RenderObject:
        texture = sdl2.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_RGBA8888, sdl2.SDL_TEXTUREACCESS_TARGET, 1, 1)
        sdl2.SDL_SetRenderTarget(renderer, texture)
        sdl2.SDL_SetRenderDrawColor(renderer, color.r, color.g, color.b, color.a)
        sdl2.SDL_RenderClear(renderer)
        sdl2.SDL_SetRenderTarget(renderer, None)
        return RenderObject(texture)

    @classmethod
    def render_object_from_file(cls, renderer: sdl2.SDL_Renderer, path: bytes) -> RenderObject:
        surface = sdl2.sdlimage.IMG_Load(path)
        if not surface:
            raise RuntimeError("Unable to load image "
                               + str(path)
                               + "! SDL_image Error: "
                               + str(sdl2.sdlimage.IMG_GetError()))

        render_object = cls.render_object_from_surface(renderer, surface)
        sdl2.SDL_FreeSurface(surface)
        return render_object

    @classmethod
    def render_object_from_file_with_frame(
            cls,
            renderer: sdl2.SDL_Renderer,
            path: bytes,
            frame_size: sdl2.SDL_Rect
    ) -> RenderObject:
        render_object = cls.render_object_from_file(renderer, path)
        render_object.renderFrameSize = frame_size
        render_object.fullRender = False
        return render_object

    def render(
            self,
            context: GameContext,
            position: Vector2D,
            size: Size,
            camera_position: Vector2D,
            camera_size: Size
    ) -> None:
        render_position = position \
                          + Vector2D(-size.width / 2, -size.height / 2) \
                          - camera_position \
                          - Vector2D(-camera_size.width / 2, -camera_size.height / 2)

        rect = sdl2.SDL_Rect()
        rect.x = round(context.settings.windowWidth * (render_position.x / camera_size.width))
        rect.y = round(context.settings.windowHeight * (render_position.y / camera_size.height))
        rect.w = round(context.settings.windowWidth * (size.width / camera_size.width))
        rect.h = round(context.settings.windowHeight * (size.height / camera_size.height))
        render_frame = None
        if not self.fullRender:
            render_frame = self.renderFrameSize
        sdl2.SDL_RenderCopyEx(context.renderer, self.texture, render_frame, rect, 0, None, self.renderFlip)
