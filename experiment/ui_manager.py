"""
UI Manager for the Bill Splitter application.
Coordinates all user interface elements and state management.
"""
import pygame
import os
from contextlib import contextmanager

# Import from local modules - using try/except for better error messages
try:
    from constants import (
        WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
        WHITE, BLACK, GRAY, LIGHT_GRAY, DARK_GRAY,
        BLUE, LIGHT_BLUE, GREEN, RED,
        STATE_MENU, STATE_ADD_DISHES, STATE_ADD_PEOPLE,
        STATE_ASSIGN_ORDERS, STATE_RESULTS, STATE_FILE_SAVED
    )
except ImportError as e:
    print(f"ERROR: Cannot import constants.py")
    print(f"Make sure constants.py is in the same folder as this file.")
    print(f"Error details: {e}")
    raise

try:
    from ui_components import Button, InputBox, safe_draw
except ImportError as e:
    print(f"ERROR: Cannot import ui_components.py")
    print(f"Make sure ui_components.py is in the same folder as this file.")
    print(f"Error details: {e}")
    raise

try:
    from input_collector import InputCollector
except ImportError as e:
    print(f"ERROR: Cannot import input_collector.py")
    print(f"Make sure input_collector.py is in the same folder as this file.")
    print(f"Error details: {e}")
    raise

try:
    from bill_calculator import BillCalculator
except ImportError as e:
    print(f"ERROR: Cannot import bill_calculator.py")
    print(f"Make sure bill_calculator.py is in the same folder as this file.")
    print(f"Error details: {e}")
    raise

try:
    from output_manager import OutputManager
except ImportError as e:
    print(f"ERROR: Cannot import output_manager.py")
    print(f"Make sure output_manager.py is in the same folder as this file.")
    print(f"Error details: {e}")
    raise


@contextmanager
def rendering_context(surface: pygame.Surface, color=None):
    """Context manager for safe rendering operations."""
    if color is None:
        color = WHITE
    try:
        surface.fill(color)
        yield surface
        pygame.display.flip()
    except Exception as e:
        print(f"Rendering error: {e}")
        raise


class UIManager:
    """Main UI manager coordinating the application interface."""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Bill Splitter App")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialize fonts
        self.title_font = pygame.font.Font(None, 56)
        self.header_font = pygame.font.Font(None, 42)
        self.normal_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        # Initialize components
        self.input_collector = InputCollector()
        self.state = STATE_MENU
        self.saved_filename = None
        self.dish_rects = {}

        self._setup_ui_components()

    def _setup_ui_components(self):
        """Initialize all UI components."""
        # Input boxes
        self.dish_name_input = InputBox(50, 200, 350, 50, "Dish name...")
        self.dish_price_input = InputBox(450, 200, 250, 50, "Price (THB)...", numeric_only=True)
        self.person_name_input = InputBox(50, 200, 600, 50, "Person name...")

        # Buttons
        self.start_button = Button(300, 300, 300, 60, "Start Bill Split", GREEN)
        self.add_dish_button = Button(720, 200, 150, 50, "Add Dish", GREEN)
        self.add_person_button = Button(670, 200, 200, 50, "Add Person", GREEN)
        self.next_button = Button(650, 600, 200, 60, "Next", BLUE)
        self.back_button = Button(50, 600, 200, 60, "Back", GRAY)
        self.calculate_button = Button(300, 600, 300, 60, "Calculate Bills", GREEN)
        self.restart_button = Button(300, 600, 300, 60, "Start Over", BLUE)

    @safe_draw
    def _draw_menu_screen(self):
        """Draw the main menu screen."""
        title = self.title_font.render("Bill Splitter", True, BLUE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        subtitle = self.normal_font.render("Split your restaurant bill fairly", True, DARK_GRAY)
        subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220))
        self.screen.blit(subtitle, subtitle_rect)

        self.start_button.draw(self.screen)

        instructions = [
            "1. Add dishes",
            "2. Add people",
            "3. Map Name and Dish",
            "4. Get results!"
        ]
        y = 400
        for instruction in instructions:
            text = self.normal_font.render(instruction, True, BLACK)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 40

    @safe_draw
    def _draw_add_dishes_screen(self):
        """Draw the add dishes screen."""
        header = self.header_font.render("Add Dishes", True, BLUE)
        self.screen.blit(header, (50, 50))

        instruction = self.small_font.render("Enter dish name & price", True, DARK_GRAY)
        self.screen.blit(instruction, (50, 120))

        self.dish_name_input.draw(self.screen)
        self.dish_price_input.draw(self.screen)
        self.add_dish_button.draw(self.screen)

        # Display added dishes
        y = 280
        dishes_header = self.normal_font.render(
            f"Dishes ({len(self.input_collector.dishes)}):", 
            True, 
            BLACK
        )
        self.screen.blit(dishes_header, (50, y))

        y += 50
        for dish in list(self.input_collector.dishes.values())[:8]:
            dish_text = self.small_font.render(f"• {dish.get_info()}", True, BLACK)
            self.screen.blit(dish_text, (70, y))
            y += 35

        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def _draw_add_people_screen(self):
        """Draw the add people screen."""
        header = self.header_font.render("Add People", True, BLUE)
        self.screen.blit(header, (50, 50))

        instruction = self.small_font.render("Enter each person's name", True, DARK_GRAY)
        self.screen.blit(instruction, (50, 120))

        self.person_name_input.draw(self.screen)
        self.add_person_button.draw(self.screen)

        # Display added people
        y = 280
        people_header = self.normal_font.render(
            f"People ({len(self.input_collector.people)}):", 
            True, 
            BLACK
        )
        self.screen.blit(people_header, (50, y))

        y += 50
        for person in list(self.input_collector.people.values())[:10]:
            text = self.small_font.render(f"• {person.name}", True, BLACK)
            self.screen.blit(text, (70, y))
            y += 35

        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def _draw_assign_orders_screen(self):
        """Draw the dish assignment screen."""
        current_person = self.input_collector.get_current_person()
        
        if not current_person:
            return

        header = self.header_font.render(
            f"Map Name and Dish for {current_person.name}", 
            True, 
            BLUE
        )
        self.screen.blit(header, (50, 50))

        # Draw selectable dishes
        y = 170
        self.dish_rects = {}
        
        for dish in self.input_collector.dishes.values():
            rect = pygame.Rect(50, y, 800, 40)
            self.dish_rects[dish.name] = rect

            is_selected = dish.name in self.input_collector.selected_dishes
            color = LIGHT_BLUE if is_selected else LIGHT_GRAY

            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2, border_radius=5)

            check = "(selected) " if is_selected else "  "
            text = self.normal_font.render(check + dish.get_info(), True, BLACK)
            self.screen.blit(text, (60, y + 5))
            y += 50

        # Update button text
        self.next_button.text = "Finish" if self.input_collector.is_last_person() else "Next Person"
        
        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def _draw_file_saved_screen(self):
        """Draw the file saved confirmation screen."""
        header = self.header_font.render(
            "The result file has been created!", 
            True, 
            GREEN
        )
        self.screen.blit(header, (50, 50))

        if self.saved_filename:
            try:
                path = OutputManager.get_file_absolute_path(self.saved_filename)
                info_text = f"File: {self.saved_filename}"
                path_text = f"Address: {path}" if path else "Address: (unable to determine)"
                
                info_surface = self.normal_font.render(info_text, True, BLACK)
                path_surface = self.small_font.render(path_text, True, DARK_GRAY)
                
                self.screen.blit(info_surface, (50, 150))
                self.screen.blit(path_surface, (50, 200))
            except Exception as e:
                error_text = self.normal_font.render(f"Error: {e}", True, RED)
                self.screen.blit(error_text, (50, 150))

        self.restart_button.draw(self.screen)

    @safe_draw
    def _draw_results_screen(self):
        """Draw the results summary screen."""
        header = self.header_font.render("Bill Summary", True, GREEN)
        self.screen.blit(header, (50, 30))

        # Display individual amounts
        y = 100
        for person in self.input_collector.people.values():
            text = self.normal_font.render(
                OutputManager.format_person_summary(person.name, person.total),
                True,
                BLACK
            )
            self.screen.blit(text, (50, y))
            y += 45

        # Display total
        total_bill = BillCalculator.get_total_bill(self.input_collector.dishes)
        y += 20
        pygame.draw.line(self.screen, DARK_GRAY, (50, y), (WINDOW_WIDTH - 50, y), 2)
        y += 30

        total_text = self.header_font.render(
            f"Total: {OutputManager.format_currency(total_bill)}", 
            True, 
            BLUE
        )
        self.screen.blit(total_text, (50, y))

        # Payment reminder
        reminder = self.normal_font.render("PLEASE PAY NA KRUB", True, RED)
        reminder_rect = reminder.get_rect(center=(WINDOW_WIDTH // 2, 530))
        self.screen.blit(reminder, reminder_rect)

        self.restart_button.draw(self.screen)

    def _handle_menu_events(self, event):
        """Handle events on the menu screen."""
        if self.start_button.handle_event(event):
            self.state = STATE_ADD_DISHES

    def _handle_add_dishes_events(self, event):
        """Handle events on the add dishes screen."""
        self.dish_name_input.handle_event(event)
        self.dish_price_input.handle_event(event)
        
        if self.add_dish_button.handle_event(event):
            if self.input_collector.add_dish(
                self.dish_name_input.get_text(),
                self.dish_price_input.get_text()
            ):
                self.dish_name_input.clear()
                self.dish_price_input.clear()
        
        if self.next_button.handle_event(event) and self.input_collector.has_dishes():
            self.state = STATE_ADD_PEOPLE
        
        if self.back_button.handle_event(event):
            self.state = STATE_MENU

    def _handle_add_people_events(self, event):
        """Handle events on the add people screen."""
        self.person_name_input.handle_event(event)
        
        if self.add_person_button.handle_event(event):
            if self.input_collector.add_person(self.person_name_input.get_text()):
                self.person_name_input.clear()
        
        if self.next_button.handle_event(event) and self.input_collector.has_people():
            self.state = STATE_ASSIGN_ORDERS
            self.input_collector.current_person_index = 0
            self.input_collector.selected_dishes = []
        
        if self.back_button.handle_event(event):
            self.state = STATE_ADD_DISHES

    def _handle_assign_orders_events(self, event):
        """Handle events on the assign orders screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            for dish_name, rect in self.dish_rects.items():
                if rect.collidepoint(event.pos):
                    self.input_collector.toggle_dish_selection(dish_name)

        if self.next_button.handle_event(event):
            has_more = self.input_collector.advance_to_next_person()
            
            if not has_more:
                BillCalculator.calculate_bills(
                    self.input_collector.dishes,
                    self.input_collector.people
                )
                self.saved_filename = OutputManager.save_bill_to_file(
                    self.input_collector.dishes,
                    self.input_collector.people
                )
                self.state = STATE_FILE_SAVED

        if self.back_button.handle_event(event):
            self.state = STATE_ADD_PEOPLE

    def _handle_results_events(self, event):
        """Handle events on the results screens."""
        if self.restart_button.handle_event(event):
            self.input_collector.reset()
            self.state = STATE_MENU
            self.saved_filename = None

    def handle_events(self):
        """Main event handling dispatcher."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == STATE_MENU:
                self._handle_menu_events(event)
            elif self.state == STATE_ADD_DISHES:
                self._handle_add_dishes_events(event)
            elif self.state == STATE_ADD_PEOPLE:
                self._handle_add_people_events(event)
            elif self.state == STATE_ASSIGN_ORDERS:
                self._handle_assign_orders_events(event)
            elif self.state in [STATE_RESULTS, STATE_FILE_SAVED]:
                self._handle_results_events(event)

    def draw(self):
        """Main drawing dispatcher."""
        with rendering_context(self.screen):
            if self.state == STATE_MENU:
                self._draw_menu_screen()
            elif self.state == STATE_ADD_DISHES:
                self._draw_add_dishes_screen()
            elif self.state == STATE_ADD_PEOPLE:
                self._draw_add_people_screen()
            elif self.state == STATE_ASSIGN_ORDERS:
                self._draw_assign_orders_screen()
            elif self.state == STATE_FILE_SAVED:
                self._draw_file_saved_screen()
            elif self.state == STATE_RESULTS:
                self._draw_results_screen()

    def run(self):
        """Main application loop."""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)