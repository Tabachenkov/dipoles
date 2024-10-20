import pygame
from pygame import gfxdraw
from dataclasses import dataclass, field
from domain import *


def pygame_mouse_get_clicked() -> bool:
    return pygame.mouse.get_pressed() == (1, 0, 0)


def pygame_mouse_get_pos() -> Position:
    return Position(*pygame.mouse.get_pos())


def pygame_rect_collides_pos(rect: Rectangle, pos: Position) -> bool:
    return pygame.Rect(*rect).collidepoint(pos)


def pygame_vector_from_pos(pos: Position) -> pygame.Vector2:
    return pygame.Vector2(pos.x, pos.y)


def pygame_draw_text(
        surface: pygame.Surface, 
        text: str, 
        font: pygame.font.Font,
        color: Color,
        pos: Position, 
        ort: PositionOrientation = PositionOrientation.TOP_LEFT
):
    text_surface = font.render(text, True, color.rgb)
    text_rect = Rectangle(*text_surface.get_rect())
    pos = orient_pos(pos, text_rect.size, ort, PositionOrientation.TOP_LEFT)
    surface.blit(text_surface, pos)


def pygame_draw_filled_circle(surface: pygame.Surface, pos: Position, radius: int, color: Color):
    gfxdraw.aacircle(
        surface,
        pos.x,
        pos.y,
        radius,
        color.rgb,
    )
    gfxdraw.filled_circle(
        surface,
        pos.x,
        pos.y,
        radius,
        color.rgb
    )
    

def pygame_draw_arrow(
        surface: pygame.Surface,
        start: pygame.Vector2,
        end: pygame.Vector2,
        color: pygame.Color,
        body_width: int = 2,
        head_width: int = 4,
        head_height: int = 2,
    ):
    """Draw an arrow between start and end with the arrow head at the end.

    Args:
        surface (pygame.Surface): The surface to draw on
        start (pygame.Vector2): Start position
        end (pygame.Vector2): End position
        color (pygame.Color): Color of the arrow
        body_width (int, optional): Defaults to 2.
        head_width (int, optional): Defaults to 4.
        head_height (float, optional): Defaults to 2.
    """
    arrow = start - end
    angle = arrow.angle_to(pygame.Vector2(0, -1))
    body_length = arrow.length() - head_height

    # Create the triangle head around the origin
    head_verts = [
        pygame.Vector2(0, head_height / 2),  # Center
        pygame.Vector2(head_width / 2, -head_height / 2),  # Bottomright
        pygame.Vector2(-head_width / 2, -head_height / 2),  # Bottomleft
    ]
    # Rotate and translate the head into place
    translation = pygame.Vector2(0, arrow.length() - (head_height / 2)).rotate(-angle)
    for i in range(len(head_verts)):
        head_verts[i].rotate_ip(-angle)
        head_verts[i] += translation
        head_verts[i] += start

    pygame.draw.polygon(surface, color, head_verts)

    # Stop weird shapes when the arrow is shorter than arrow head
    if arrow.length() >= head_height:
        # Calculate the body rect, rotate and translate into place
        body_verts = [
            pygame.Vector2(-body_width / 2, body_length / 2),  # Topleft
            pygame.Vector2(body_width / 2, body_length / 2),  # Topright
            pygame.Vector2(body_width / 2, -body_length / 2),  # Bottomright
            pygame.Vector2(-body_width / 2, -body_length / 2),  # Bottomleft
        ]
        translation = pygame.Vector2(0, body_length / 2).rotate(-angle)
        for i in range(len(body_verts)):
            body_verts[i].rotate_ip(-angle)
            body_verts[i] += translation
            body_verts[i] += start

        pygame.draw.polygon(surface, color, body_verts)


def pygame_surface_to_np_array(surface: pygame.Surface):
    return pygame.surfarray.array3d(surface).transpose([1, 0, 2])


@dataclass
class PygameButtonBase:
    surface: pygame.Surface
    rect: Rectangle
    background_color: Color
    hover_background_color: Color | None
    hold_background_color: Color | None
    _holding: bool = field(init=False, default=False)


    def _hovered(self) -> bool:
        return pygame_rect_collides_pos(self.rect, pygame_mouse_get_pos())

    def draw(self) -> None:
        color = self.background_color
        if self.hover_background_color is not None and self._hovered():
            color = self.hover_background_color
        if self.hold_background_color is not None and self._holding:
            color = self.hold_background_color
        pygame.draw.rect(self.surface, color.rgb, self.rect)
    
    def pressed(self) -> bool:
        if self._hovered():
            if pygame_mouse_get_clicked():
                if not self._holding:
                    self._holding = True
            else:
                if self._holding:
                    self._holding = False
                    return True
        else:
            self._holding = False
        return False


@dataclass
class PygameTextButton(PygameButtonBase):
    text: str
    text_color: Color
    font: pygame.font.Font

    def draw(self) -> None:
        super().draw()
        pygame_draw_text(
            surface=self.surface,
            text=self.text,
            font=self.font,
            color=self.text_color,
            pos=self.rect.get_oriented_pos(PositionOrientation.MIDDLE_MIDDLE),
            ort=PositionOrientation.MIDDLE_MIDDLE
        )


@dataclass
class PygameImageButton(PygameButtonBase):
    image_surface: pygame.Surface

    def draw(self) -> None:
        super().draw()
        self.surface.blit(self.image_surface, self.rect.top_left_pos)


@dataclass
class PygameCheckboxButton(PygameButtonBase):
    image_surface: pygame.Surface
    active: bool = field(init=False, default=False)

    def draw(self) -> None:
        super().draw()
        if self.active:
            self.surface.blit(self.image_surface, self.rect.top_left_pos)