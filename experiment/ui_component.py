"""
UI components for the Bill Splitter application.
Contains reusable interface elements.
"""
import pygame
from abc import ABC, abstractmethod
from constants import *

def safe_draw(func):
    """Decorator to handle drawing errors gracefully."""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print(f"Drawing error in {func.__name__}: {e}")
    return wrapper


class UIComponent(ABC):
    """Abstract base class for UI components."""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component on the given surface."""
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.
        
        Returns:
            True if the event was consumed/acted upon, False otherwise
        """
        pass


class Button(UIComponent):
    """Interactive button component."""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        w: int, 
        h: int, 
        text: str, 
        color=BLUE, 
        text_color=WHITE
    ):
        super().__init__(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = LIGHT_BLUE
        self.text_color = text_color
        self.hovered = False
        self.font = pygame.font.Font(None, 32)

    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button with hover effect."""
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse hover and click events."""
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class InputBox(UIComponent):
    """Text input box component with validation."""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        w: int, 
        h: int, 
        placeholder: str = "", 
        numeric_only: bool = False
    ):
        super().__init__(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.numeric_only = numeric_only
        self.font = pygame.font.Font(None, 32)
        self.color_inactive = GRAY
        self.color_active = BLUE

    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the input box with text or placeholder."""
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)

        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else DARK_GRAY

        text_surface = self.font.render(display_text, True, text_color)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse click and keyboard input."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                char = event.unicode
                if self.numeric_only:
                    if char.isdigit() or char == '.':
                        if char == '.' and '.' in self.text:
                            return False
                        self.text += char
                else:
                    if char.isprintable():
                        self.text += char
        return False

    def clear(self) -> None:
        """Clear the input text."""
        self.text = ""

    def get_text(self) -> str:
        """Get the current text value."""
        return self.text


class Label:
    """Simple text label component."""
    
    def __init__(
        self, 
        x: int, 
        y: int, 
        text: str, 
        font_size: int = 32, 
        color=BLACK
    ):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, font_size)

    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the label text."""
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.x, self.y))

    def set_text(self, text: str) -> None:
        """Update the label text."""
        self.text = text