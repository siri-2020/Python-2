"""
Bill Splitter Application

A Pygame-based application for splitting restaurant bills
fairly among multiple people.
"""

import pygame
import sys
import os
import datetime
from abc import ABC, abstractmethod
from contextlib import contextmanager

# =============== User Interface ==================

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 700
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
BLUE = (66, 133, 244)
LIGHT_BLUE = (100, 160, 255)
GREEN = (52, 168, 83)
RED = (234, 67, 53)
YELLOW = (251, 188, 5)

# Game States
STATE_MENU = 0
STATE_ADD_DISHES = 1
STATE_ADD_PEOPLE = 2
STATE_ASSIGN_ORDERS = 3
STATE_RESULTS = 4
STATE_FILE_SAVED = 5


def safe_draw(func):
    """
    Decorator to catch and log drawing errors.
    
    Prevents the application from crashing due to
    rendering issues.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as error:
            print(f"Drawing error in {func.__name__}: {error}")
    return wrapper


class UIComponent(ABC):
    """
    Abstract base class for UI components.
    
    All UI elements should inherit from this class.
    """
    
    def __init__(
        self,
        position_x: int,
        position_y: int,
        width: int,
        height: int
    ) -> None:
        """Initialize UI component with position and size."""
        self.rect = pygame.Rect(
            position_x,
            position_y,
            width,
            height
        )
        self.visible = True

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component on the given surface."""
        pass

    @abstractmethod
    def handle_event(
        self,
        event: pygame.event.Event
    ) -> bool:
        """Handle pygame events and return True if acted upon."""
        pass


class Button(UIComponent):
    """
    Interactive button component.
    
    Supports hover effects and click detection.
    """
    
    def __init__(
        self,
        position_x: int,
        position_y: int,
        width: int,
        height: int,
        text: str,
        color: tuple = BLUE,
        text_color: tuple = WHITE
    ) -> None:
        """Initialize button with text and colors."""
        super().__init__(position_x, position_y, width, height)
        self.text = text
        self.color = color
        self.hover_color = LIGHT_BLUE
        self.text_color = text_color
        self.hovered = False
        self.font = pygame.font.Font(None, 32)

    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw button with hover effect."""
        current_color = (
            self.hover_color if self.hovered else self.color
        )
        pygame.draw.rect(
            surface,
            current_color,
            self.rect,
            border_radius=8
        )
        pygame.draw.rect(
            surface,
            DARK_GRAY,
            self.rect,
            2,
            border_radius=8
        )

        text_surface = self.font.render(
            self.text,
            True,
            self.text_color
        )
        text_rect = text_surface.get_rect(
            center=self.rect.center
        )
        surface.blit(text_surface, text_rect)

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle mouse events for button interaction.
        
        Returns True when button is clicked.
        """
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class InputBox(UIComponent):
    """
    Text input box component.
    
    Supports placeholder text and numeric-only mode.
    """
    
    def __init__(
        self,
        position_x: int,
        position_y: int,
        width: int,
        height: int,
        placeholder: str = "",
        numeric_only: bool = False
    ) -> None:
        """Initialize input box with optional constraints."""
        super().__init__(position_x, position_y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.numeric_only = numeric_only
        self.font = pygame.font.Font(None, 32)
        self.color_inactive = GRAY
        self.color_active = BLUE

    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw input box with current text or placeholder."""
        current_color = (
            self.color_active if self.active
            else self.color_inactive
        )
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(
            surface,
            current_color,
            self.rect,
            2,
            border_radius=5
        )

        display_text = (self.text if self.text else self.placeholder)
        text_color = BLACK if self.text else DARK_GRAY

        text_surface = self.font.render(display_text, True, text_color)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle keyboard and mouse events for input.
        
        Returns True when Enter is pressed.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            return self.active

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                character = event.unicode
                if self.numeric_only:
                    if character.isdigit() or character == '.':
                        if (character == '.'
                                and '.' in self.text):
                            return False
                        self.text += character
                else:
                    if character.isprintable():
                        self.text += character
        return False

@contextmanager
def rendering_context(surface: pygame.Surface,
        background_color: tuple = WHITE):
    """Context manager for safe rendering operations."""
    try:
        surface.fill(background_color)
        yield surface
        pygame.display.flip()
    except Exception as error:
        print(f"Rendering error: {error}")
        raise

# ================== Models ===================
class MenuItem(ABC):
    """
    Abstract base class for menu items.
    
    Represents items that can be ordered.
    """
    
    def __init__(self, name: str, price: float) -> None:
        """Initialize menu item with name and price."""
        self._name = name
        self._price = price

    @property
    def name(self) -> str:
        """Get the item name."""
        return self._name

    @property
    def price(self) -> float:
        """Get the item price."""
        return self._price

    @abstractmethod
    def get_info(self) -> str:
        """Return formatted information about the item."""
        pass


class Dish(MenuItem):
    """
    Represents a dish that can be shared among people.
    
    Tracks who is eating the dish for bill splitting.
    """
    
    def __init__(self, name: str, price: float) -> None:
        """Initialize dish with name and price."""
        super().__init__(name, price)
        self._eaters: list[str] = []

    @property
    def eaters(self) -> list[str]:
        """Get list of people eating this dish."""
        return self._eaters

    def add_eater(self, person_name: str) -> None:
        """Add a person to the list of eaters."""
        if person_name not in self._eaters:
            self._eaters.append(person_name)

    def get_shared_price(self) -> float:
        """
        Calculate price per person for this dish.
        
        Returns 0 if no one is eating the dish.
        """
        if len(self._eaters) == 0:
            return 0.0
        return self._price / len(self._eaters)

    def get_info(self) -> str:
        """Return formatted dish information."""
        return f"{self.name}: THB {self.price:.2f}"


class Person:
    """
    Represents a person splitting the bill.
    
    Tracks their name and total amount owed.
    """
    
    def __init__(self, name: str) -> None:
        """Initialize person with name."""
        self._name = name.strip()
        self._total = 0.0

    @property
    def name(self) -> str:
        """Get the person's name."""
        return self._name

    @property
    def total(self) -> float:
        """Get the person's total bill amount."""
        return self._total

    def add_to_total(self, amount: float) -> None:
        """Add an amount to the person's total."""
        self._total += amount


def dish_iterator(dishes: dict[str, Dish]):
    """
    Iterator for dishes dictionary.
    
    Yields dish objects from the dictionary.
    """
    for dish in dishes.values():
        yield dish

# ================= Bill Calculation =================
class BillSplitterApp:
    """
    Main application class for bill splitting.
    
    Manages UI, state, and bill calculation logic.
    """
    
    def __init__(self) -> None:
        """Initialize the application."""
        self.screen = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT)
        )
        pygame.display.set_caption("Bill Splitter App")
        self.clock = pygame.time.Clock()
        self.running = True

        # Image
        self.qr_image = pygame.image.load("qr_code.jpg")
        self.qr_image = pygame.transform.scale(self.qr_image, (250, 250))

        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.header_font = pygame.font.Font(None, 42)
        self.normal_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        # Data
        self.dishes: dict[str, Dish] = {}
        self.people: dict[str, Person] = {}
        self.current_person_index = 0
        self.selected_dishes: list[str] = []
        self.saved_filename: str = None

        self.state = STATE_MENU
        self.scroll_offset = 0

        self.setup_ui()

    def setup_ui(self) -> None:
        """Initialize all UI components."""
        self.dish_name_input = InputBox(
            50, 200, 350, 50, "Dish name..."
        )
        self.dish_price_input = InputBox(
            450, 200, 250, 50,
            "Price (THB)...",
            numeric_only=True
        )
        self.person_name_input = InputBox(
            50, 200, 600, 50, "Person name..."
        )

        self.start_button = Button(
            300, 300, 300, 60,
            "Start Bill Split",
            GREEN
        )
        self.add_dish_button = Button(
            720, 200, 150, 50, "Add Dish", GREEN
        )
        self.next_button = Button(
            650, 600, 200, 60, "Next", BLUE
        )
        self.back_button = Button(
            50, 600, 200, 60, "Back", GRAY
        )
        self.add_person_button = Button(
            670, 200, 200, 50, "Add Person", GREEN
        )
        self.save_button = Button(
            300, 600, 300, 60, "Save Bill Summary to File", GREEN
        )
        self.restart_button = Button(
            200, 600, 200, 60, "Start Over", BLUE
        )
        self.quit_button = Button(
            500, 600, 200, 60, "Quit", RED
        )

    def save_results_to_file(self) -> str:
        """
        Save bill summary to a timestamped file.
        
        Returns the filename if successful, None otherwise.
        """
        try:
            # Create bills_archive folder if it doesn't exist
            archive_folder = "bills_archive"
            if not os.path.exists(archive_folder):
                os.makedirs(archive_folder)
            
            current_time = datetime.datetime.now()
            timestamp = current_time.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"bill_{timestamp}.txt"
            file_path = os.path.join(archive_folder, filename)

            with open(
                file_path, "w", encoding="utf-8"
            ) as file_handle:
                file_handle.write("===== Bill Summary =====\n")
                file_handle.write(f"Created: {timestamp}\n\n")
                for person in self.people.values():
                    file_handle.write(
                        f"{person.name}: "
                        f"THB {person.total:.2f}\n"
                    )
                total_bill = sum(dish.price for dish in self.dishes.values())
                file_handle.write(f"\nTotal Bill: {total_bill:.2f} Baht\n")
                file_handle.write("=========================\n\n")

            print(f"Bill saved to {file_path}")
            return file_path
        except Exception as error:
            print(f"Error saving bill: {error}")
            return None

    @safe_draw
    def draw_menu_screen(self) -> None:
        """Draw the main menu screen."""
        title = self.title_font.render("Bill Splitter",
            True,
            BLUE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        subtitle = self.normal_font.render(
            "Split your restaurant bill fairly",
            True,
            DARK_GRAY
        )
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)
        self.start_button.draw(self.screen)

        instructions = [
            "1. Add dishes",
            "2. Add people",
            "3. Map Name and Dish",
            "4. Get results!"
        ]
        vertical_position = 400
        for instruction_text in instructions:
            text = self.normal_font.render(instruction_text,
                True,
                BLACK)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2,
                                    vertical_position))
            self.screen.blit(text, rect)
            vertical_position += 40

    @safe_draw
    def draw_add_dishes_screen(self) -> None:
        """Draw the add dishes screen."""

        header = self.header_font.render("Add Dishes", True, BLUE)
        self.screen.blit(header, (50, 50))
        instruction = self.small_font.render("Enter dish name & price",
            True,
            DARK_GRAY)
        self.screen.blit(instruction, (50, 120))
        self.dish_name_input.draw(self.screen)
        self.dish_price_input.draw(self.screen)
        self.add_dish_button.draw(self.screen)

        vertical_position = 280
        dishes_header = self.normal_font.render(
            f"Dishes ({len(self.dishes)}):",
            True,
            BLACK
        )
        self.screen.blit(dishes_header, (50, vertical_position))

        vertical_position += 50
        for dish in list(self.dishes.values())[:8]:
            dish_text = self.small_font.render(
                f"• {dish.get_info()}",
                True,
                BLACK
            )
            self.screen.blit(dish_text, (70, vertical_position))
            vertical_position += 35

        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def draw_add_people_screen(self) -> None:
        """Draw the add people screen."""
        header = self.header_font.render(
            "Add People", True, BLUE
        )
        self.screen.blit(header, (50, 50))

        instruction = self.small_font.render(
            "Enter each person's name",
            True,
            DARK_GRAY
        )
        self.screen.blit(instruction, (50, 120))

        self.person_name_input.draw(self.screen)
        self.add_person_button.draw(self.screen)

        vertical_position = 280
        people_header = self.normal_font.render(
            f"People ({len(self.people)}):",
            True,
            BLACK
        )
        self.screen.blit(people_header, (50, vertical_position))

        vertical_position += 50
        for person in list(self.people.values())[:10]:
            person_text = self.small_font.render(
                f"• {person.name}",
                True,
                BLACK
            )
            self.screen.blit(person_text, (70, vertical_position))
            vertical_position += 35

        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def draw_assign_orders_screen(self) -> None:
        """Draw the order assignment screen."""
        if not self.people:
            return

        people_list = list(self.people.values())
        if self.current_person_index >= len(people_list):
            self.calculate_bills()
            self.state = STATE_RESULTS
            return

        current_person = people_list[
            self.current_person_index
        ]

        header = self.header_font.render(
            f"Map Name and Dish for {current_person.name}",
            True,
            BLUE
        )
        self.screen.blit(header, (50, 50))

        vertical_position = 170
        self.dish_rects = {}
        for dish in list(self.dishes.values()):
            dish_rect = pygame.Rect(50, vertical_position, 800, 40)
            self.dish_rects[dish.name] = dish_rect

            is_selected = (dish.name in self.selected_dishes)
            rect_color = (LIGHT_BLUE if is_selected else LIGHT_GRAY)

            pygame.draw.rect(
                self.screen,
                rect_color,
                dish_rect,
                border_radius=5
            )
            pygame.draw.rect(
                self.screen,
                DARK_GRAY,
                dish_rect,
                2,
                border_radius=5
            )

            selection_indicator = (
                "(selected) " if is_selected else "  "
            )
            text = self.normal_font.render(
                selection_indicator + dish.get_info(),
                True,
                BLACK
            )
            self.screen.blit(
                text,
                (60, vertical_position + 5)
            )
            vertical_position += 50

        is_last_person = (
            self.current_person_index >= len(self.people) - 1
        )
        self.next_button.text = (
            "Finish" if is_last_person else "Next Person"
        )
        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def draw_file_saved_screen(self, filename: str) -> None:
        """Draw the file saved confirmation screen."""
        header = self.header_font.render(
            "The result file has been created!",
            True,
            GREEN
        )
        self.screen.blit(header, (50, 50))

        if filename:
            try:
                file_path = os.path.abspath(filename)
                info_text = f"File: {filename}"
                path_text = f"Address: {file_path}"
                info_surface = self.normal_font.render(
                    info_text,
                    True,
                    BLACK
                )
                path_surface = self.small_font.render(
                    path_text,
                    True,
                    DARK_GRAY
                )
                self.screen.blit(info_surface, (50, 150))
                self.screen.blit(path_surface, (50, 200))
            except Exception as error:
                error_text = self.normal_font.render(
                    f"Error showing path: {error}",
                    True,
                    RED
                )
                self.screen.blit(error_text, (50, 150))

        self.restart_button.draw(self.screen)
        self.quit_button.draw(self.screen)

    @safe_draw
    def draw_results_screen(self) -> None:
        """Draw the bill summary results screen."""
        header = self.header_font.render(
            "Bill Summary", True, GREEN
        )
        self.screen.blit(header, (50, 30))

        vertical_position = 100
        for person in self.people.values():
            person_total_text = self.normal_font.render(
                f"{person.name}: THB {person.total:.2f}",
                True,
                BLACK
            )
            self.screen.blit(
                person_total_text,
                (50, vertical_position)
            )
            vertical_position += 45

        total_bill = sum(
            dish.price for dish in self.dishes.values()
        )
        vertical_position += 20
        pygame.draw.line(
            self.screen,
            DARK_GRAY,
            (50, vertical_position),
            (WINDOW_WIDTH - 50, vertical_position),
            2
        )
        vertical_position += 30

        total_text = self.header_font.render(
            f"Total: THB {total_bill:.2f}",
            True,
            BLUE
        )
        self.screen.blit(total_text, (50, vertical_position))

        thank_you_message = self.normal_font.render(
            "PLEASE PAY NA KRUB", True, RED
        )
        thank_you_rect = thank_you_message.get_rect(
            center=(WINDOW_WIDTH // 2, 530)
        )
        self.screen.blit(thank_you_message, thank_you_rect)

        # === SHOW QR CODE ON RESULT PRICE PAGE ===
        if hasattr(self, "qr_image") and self.qr_image:
            qr_rect = self.qr_image.get_rect(
                center=(WINDOW_WIDTH // 2, 450)
            )
            self.screen.blit(self.qr_image, qr_rect)

        self.save_button.draw(self.screen)

    def add_dish(self) -> None:
        """
        Add a new dish from input fields.
        
        Validates name and price before adding.
        """
        dish_name = self.dish_name_input.text.strip()
        price_string = self.dish_price_input.text.strip()
        if not dish_name or not price_string:
            return
        if dish_name in self.dishes:
            return
        try:
            dish_price = float(price_string)
        except ValueError:
            return
        self.dishes[dish_name] = Dish(dish_name, dish_price)
        self.dish_name_input.text = ""
        self.dish_price_input.text = ""

    def add_person(self) -> None:
        """
        Add a new person from input field.
        
        Validates name and checks for duplicates.
        """
        person_name = self.person_name_input.text.strip()
        if not person_name or person_name in self.people:
            return
        self.people[person_name] = Person(person_name)
        self.person_name_input.text = ""

    def calculate_bills(self) -> None:
        """
        Calculate total bill for each person.
        
        Splits shared dishes evenly among eaters.
        """
        for person in self.people.values():
            person._total = 0.0
        for dish in dish_iterator(self.dishes):
            shared_price = dish.get_shared_price()
            for eater_name in dish.eaters:
                if eater_name in self.people:
                    self.people[eater_name].add_to_total(
                        shared_price
                    )

    def handle_events(self) -> None:
        """Handle all pygame events based on current state."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == STATE_MENU:
                if self.start_button.handle_event(event):
                    self.state = STATE_ADD_DISHES

            elif self.state == STATE_ADD_DISHES:
                self.dish_name_input.handle_event(event)
                self.dish_price_input.handle_event(event)
                if self.add_dish_button.handle_event(event):
                    self.add_dish()
                if (self.next_button.handle_event(event)
                        and self.dishes):
                    self.state = STATE_ADD_PEOPLE
                if self.back_button.handle_event(event):
                    self.state = STATE_MENU

            elif self.state == STATE_ADD_PEOPLE:
                self.person_name_input.handle_event(event)
                if self.add_person_button.handle_event(event):
                    self.add_person()
                if (self.next_button.handle_event(event)
                        and self.people):
                    self.state = STATE_ASSIGN_ORDERS
                    self.current_person_index = 0
                    self.selected_dishes = []
                if self.back_button.handle_event(event):
                    self.state = STATE_ADD_DISHES

            elif self.state == STATE_ASSIGN_ORDERS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for dish_name, dish_rect in (
                        self.dish_rects.items()
                    ):
                        if dish_rect.collidepoint(event.pos):
                            if (dish_name
                                    in self.selected_dishes):
                                self.selected_dishes.remove(
                                    dish_name
                                )
                            else:
                                self.selected_dishes.append(
                                    dish_name
                                )

                if self.next_button.handle_event(event):
                    people_list = list(self.people.values())
                    if (self.current_person_index
                            < len(people_list)):
                        current_person = people_list[
                            self.current_person_index
                        ]
                        for selected_dish_name in (
                            self.selected_dishes
                        ):
                            self.dishes[
                                selected_dish_name
                            ].add_eater(current_person.name)

                    self.current_person_index += 1
                    self.selected_dishes = []

                    if (self.current_person_index
                            >= len(people_list)):
                        self.calculate_bills()
                        self.state = STATE_RESULTS

                if self.back_button.handle_event(event):
                    self.state = STATE_ADD_PEOPLE

            elif self.state == STATE_RESULTS:
                if self.save_button.handle_event(event):
                    self.saved_filename = (
                        self.save_results_to_file()
                    )
                    self.state = STATE_FILE_SAVED

            elif self.state == STATE_FILE_SAVED:
                if self.restart_button.handle_event(event):
                    self.__init__()
                elif self.quit_button.handle_event(event):
                    self.running = False

    def draw(self) -> None:
        """Draw the current screen based on state."""
        with rendering_context(self.screen):
            if self.state == STATE_MENU:
                self.draw_menu_screen()
            elif self.state == STATE_ADD_DISHES:
                self.draw_add_dishes_screen()
            elif self.state == STATE_ADD_PEOPLE:
                self.draw_add_people_screen()
            elif self.state == STATE_ASSIGN_ORDERS:
                self.draw_assign_orders_screen()
            elif self.state == STATE_FILE_SAVED:
                self.draw_file_saved_screen(
                    self.saved_filename
                )
            elif self.state == STATE_RESULTS:
                self.draw_results_screen()

    def run(self) -> None:
        """Main application loop."""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)


if __name__ == "__main__":
    app = BillSplitterApp()
    app.run()
    pygame.quit()
    sys.exit()