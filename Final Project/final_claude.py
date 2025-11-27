import pygame
import sys
from abc import ABC, abstractmethod
from contextlib import contextmanager
from enum import Enum


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


class GameState(Enum):
    """Enum for different application states"""
    MENU = 0
    ADD_DISHES = 1
    ADD_PEOPLE = 2
    ASSIGN_ORDERS = 3
    RESULTS = 4


# Decorator for error handling in draw methods
def safe_draw(func):
    """Decorator to safely handle drawing errors"""
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print(f"Drawing error in {func.__name__}: {e}")
            return None
    return wrapper


# Abstract Base Class for UI Components
class UIComponent(ABC):
    """Abstract base class for UI components"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the component"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle events, return True if event was consumed"""
        pass


class Button(UIComponent):
    """Button UI component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: tuple[int, int, int] = BLUE,
                 text_color: tuple[int, int, int] = WHITE):
        super().__init__(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = LIGHT_BLUE
        self.text_color = text_color
        self.hovered = False
        self.font = pygame.font.Font(None, 32)
    
    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the button"""
        try:
            color = self.hover_color if self.hovered else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=8)
            pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)
            
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)
        except Exception as e:
            print(f"Error: {e}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events"""
        try:
            if event.type == pygame.MOUSEMOTION:
                self.hovered = self.rect.collidepoint(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    return True
        except Exception as e:
            print(f"Error: {e}")
        return False


class InputBox(UIComponent):
    """Text input box component"""
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 placeholder: str = "", numeric_only: bool = False):
        super().__init__(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.numeric_only = numeric_only
        self.font = pygame.font.Font(None, 32)
        self.color_inactive = GRAY
        self.color_active = BLUE
    
    @safe_draw
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the input box"""
        try:
            color = self.color_active if self.active else self.color_inactive
            pygame.draw.rect(surface, WHITE, self.rect)
            pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)
            
            display_text = self.text if self.text else self.placeholder
            text_color = BLACK if self.text else DARK_GRAY
            
            text_surface = self.font.render(display_text, True, text_color)
            surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))
        except Exception as e:
            print(f"Error: {e}")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle input events"""
        try:
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
        except Exception as e:
            print(f"Error: {e}")
        return False


# Context Manager for pygame rendering
@contextmanager
def rendering_context(surface: pygame.Surface, color: tuple[int, int, int] = WHITE):
    """Context manager for rendering"""
    try:
        surface.fill(color)
        yield surface
        pygame.display.flip()
    except Exception as e:
        print(f"Rendering error: {e}")
        raise


# Abstract Base Class for Menu Items (from original code)
class MenuItem(ABC):
    """Abstract base class for menu items"""
    
    def __init__(self, name: str, price: float):
        self._name = name
        self._price = price
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def price(self) -> float:
        return self._price
    
    @abstractmethod
    def get_info(self) -> str:
        """Get item information"""
        pass


class Dish(MenuItem):
    """Concrete implementation of MenuItem for dishes"""
    
    def __init__(self, name: str, price: float):
        super().__init__(name, price)
        self._eaters: List[str] = []
    
    @property
    def eaters(self) -> list[str]:
        return self._eaters
    
    def add_eater(self, person_name: str) -> None:
        """Add a person who ate this dish"""
        try:
            if person_name not in self._eaters:
                self._eaters.append(person_name)
        except Exception as e:
            print(f"Error adding eater: {e}")
    
    def get_shared_price(self) -> float:
        """Calculate the shared price per person"""
        try:
            if len(self._eaters) == 0:
                return 0.0
            return self._price / len(self._eaters)
        except ZeroDivisionError:
            return 0.0
        except Exception as e:
            print(f"Error calculating shared price: {e}")
            return 0.0
    
    def get_info(self) -> str:
        """Get dish information"""
        return f"{self.name}: THB {self.price:.2f}"


class Person:
    """Class representing a person in the bill split"""
    
    def __init__(self, name: str):
        try:
            if not name or not name.strip():
                raise ValueError("Name cannot be empty")
            self._name = name.strip()
            self._total = 0.0
        except Exception as e:
            print(f"Error creating person: {e}")
            raise
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def total(self) -> float:
        return self._total
    
    def add_to_total(self, amount: float) -> None:
        """Add amount to person's total bill"""
        try:
            if amount < 0:
                raise ValueError("Amount cannot be negative")
            self._total += amount
        except Exception as e:
            print(f"Error adding to total: {e}")


# Generator for iterating through dishes
def dish_iterator(dishes: dict[str, Dish]):
    """Generator that yields dishes"""
    for dish in dishes.values():
        yield dish


class BillSplitterApp:
    """Main application class using Pygame"""
    
    def __init__(self):
        try:
            self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            pygame.display.set_caption("Bill Splitter App")
            self.clock = pygame.time.Clock()
            self.running = True
            
            # Fonts
            self.title_font = pygame.font.Font(None, 56)
            self.header_font = pygame.font.Font(None, 42)
            self.normal_font = pygame.font.Font(None, 32)
            self.small_font = pygame.font.Font(None, 24)
            
            # Data
            self.dishes: dict[str, Dish] = {}
            self.people: dict[str, Person] = {}
            self.current_person_index = 0
            self.selected_dishes: List[str] = []
            
            # State
            self.state = GameState.MENU
            self.scroll_offset = 0
            
            # UI Components
            self.setup_ui()
            
        except Exception as e:
            print(f"Error initializing app: {e}")
            raise
    
    def setup_ui(self) -> None:
        """Setup UI components"""
        try:
            # Input boxes
            self.dish_name_input = InputBox(50, 200, 350, 50, "Dish name...")
            self.dish_price_input = InputBox(450, 200, 250, 50, "Price (THB)...", numeric_only=True)
            self.person_name_input = InputBox(50, 200, 600, 50, "Person name...")
            
            # Buttons
            self.start_button = Button(300, 300, 300, 60, "Start Bill Split", GREEN)
            self.add_dish_button = Button(720, 200, 150, 50, "Add Dish", GREEN)
            self.next_button = Button(650, 600, 200, 60, "Next", BLUE)
            self.back_button = Button(50, 600, 200, 60, "Back", GRAY)
            self.add_person_button = Button(670, 200, 200, 50, "Add Person", GREEN)
            self.calculate_button = Button(300, 600, 300, 60, "Calculate Bills", GREEN)
            self.restart_button = Button(300, 600, 300, 60, "Start Over", BLUE)
            
        except Exception as e:
            print(f"Error setting up UI: {e}")
    
    @safe_draw
    def draw_menu_screen(self) -> None:
        """Draw the main menu screen"""
        try:
            title = self.title_font.render("Bill Splitter", True, BLUE)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
            self.screen.blit(title, title_rect)
            
            subtitle = self.normal_font.render("Split your restaurant bill fairly", True, DARK_GRAY)
            subtitle_rect = subtitle.get_rect(center=(WINDOW_WIDTH // 2, 220))
            self.screen.blit(subtitle, subtitle_rect)
            
            self.start_button.draw(self.screen)
            
            # Instructions
            instructions = [
                "1. Add dishes and prices",
                "2. Add people",
                "3. Assign who ate what",
                "4. Get the results!"
            ]
            
            y_pos = 400
            for instruction in instructions:
                text = self.normal_font.render(instruction, True, BLACK)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
                self.screen.blit(text, text_rect)
                y_pos += 50
                
        except Exception as e:
            print(f"Error drawing menu screen: {e}")
    
    @safe_draw
    def draw_add_dishes_screen(self) -> None:
        """Draw the add dishes screen"""
        try:
            # Header
            header = self.header_font.render("Add Dishes", True, BLUE)
            self.screen.blit(header, (50, 50))
            
            # Instructions
            instruction = self.small_font.render("Enter dish name and price, then click Add Dish", True, DARK_GRAY)
            self.screen.blit(instruction, (50, 120))
            
            # Input boxes
            self.dish_name_input.draw(self.screen)
            self.dish_price_input.draw(self.screen)
            self.add_dish_button.draw(self.screen)
            
            # Display added dishes
            y_pos = 280
            dishes_header = self.normal_font.render(f"Dishes ({len(self.dishes)}):", True, BLACK)
            self.screen.blit(dishes_header, (50, y_pos))
            
            y_pos += 50
            for dish in list(self.dishes.values())[:8]:  # Show max 8
                dish_text = self.small_font.render(f"• {dish.get_info()}", True, BLACK)
                self.screen.blit(dish_text, (70, y_pos))
                y_pos += 35
            
            # Navigation buttons
            self.next_button.draw(self.screen)
            self.back_button.draw(self.screen)
            
        except Exception as e:
            print(f"Error drawing add dishes screen: {e}")
    
    @safe_draw
    def draw_add_people_screen(self) -> None:
        """Draw the add people screen"""
        try:
            # Header
            header = self.header_font.render("Add People", True, BLUE)
            self.screen.blit(header, (50, 50))
            
            # Instructions
            instruction = self.small_font.render("Enter each person's name", True, DARK_GRAY)
            self.screen.blit(instruction, (50, 120))
            
            # Input box
            self.person_name_input.draw(self.screen)
            self.add_person_button.draw(self.screen)
            
            # Display added people
            y_pos = 280
            people_header = self.normal_font.render(f"People ({len(self.people)}):", True, BLACK)
            self.screen.blit(people_header, (50, y_pos))
            
            y_pos += 50
            for person in list(self.people.values())[:10]:  # Show max 10
                person_text = self.small_font.render(f"• {person.name}", True, BLACK)
                self.screen.blit(person_text, (70, y_pos))
                y_pos += 35
            
            # Navigation buttons
            self.next_button.draw(self.screen)
            self.back_button.draw(self.screen)
            
        except Exception as e:
            print(f"Error drawing add people screen: {e}")
    
    @safe_draw
    def draw_assign_orders_screen(self) -> None:
        """Draw the assign orders screen"""
        try:
            if not self.people:
                return
            
            people_list = list(self.people.values())
            if self.current_person_index >= len(people_list):
                self.state = GameState.RESULTS
                self.calculate_bills()
                return
            
            current_person = people_list[self.current_person_index]
            
            # Header
            header = self.header_font.render(f"What did {current_person.name} eat?", True, BLUE)
            self.screen.blit(header, (50, 50))
            
            # Progress
            progress = self.small_font.render(
                f"Person {self.current_person_index + 1} of {len(people_list)}", 
                True, DARK_GRAY
            )
            self.screen.blit(progress, (50, 110))
            
            # Display dishes as clickable items
            y_pos = 170
            dish_list = list(self.dishes.values())
            
            for i, dish in enumerate(dish_list):
                # Clickable area
                dish_rect = pygame.Rect(50, y_pos, 800, 40)
                
                # Check if selected
                is_selected = dish.name in self.selected_dishes
                color = LIGHT_BLUE if is_selected else LIGHT_GRAY
                
                pygame.draw.rect(self.screen, color, dish_rect, border_radius=5)
                pygame.draw.rect(self.screen, DARK_GRAY, dish_rect, 2, border_radius=5)
                
                # Store rect for click detection
                if not hasattr(self, 'dish_rects'):
                    self.dish_rects = {}
                self.dish_rects[dish.name] = dish_rect
                
                # Dish text
                dish_text = self.normal_font.render(
                    f"{'✓ ' if is_selected else '  '}{dish.get_info()}", 
                    True, BLACK
                )
                self.screen.blit(dish_text, (60, y_pos + 5))
                
                y_pos += 50
                
                if y_pos > 550:  # Limit display
                    break
            
            # Navigation buttons
            self.next_button.text = "Next Person" if self.current_person_index < len(people_list) - 1 else "Finish"
            self.next_button.draw(self.screen)
            self.back_button.draw(self.screen)
            
        except Exception as e:
            print(f"Error drawing assign orders screen: {e}")
    
    @safe_draw
    def draw_results_screen(self) -> None:
        """Draw the results screen"""
        try:
            # Header
            header = self.header_font.render("Bill Summary", True, GREEN)
            self.screen.blit(header, (50, 30))
            
            y_pos = 100
            
            # Individual bills
            for person in self.people.values():
                person_text = self.normal_font.render(
                    f"{person.name}: THB {person.total:.2f}", 
                    True, BLACK
                )
                self.screen.blit(person_text, (50, y_pos))
                y_pos += 45
            
            # Total bill
            total_bill = sum(dish.price for dish in self.dishes.values())
            y_pos += 20
            
            pygame.draw.line(self.screen, DARK_GRAY, (50, y_pos), (WINDOW_WIDTH - 50, y_pos), 2)
            y_pos += 30
            
            total_text = self.header_font.render(f"Total: THB {total_bill:.2f}", True, BLUE)
            self.screen.blit(total_text, (50, y_pos))
            
            # Thank you message
            thank_you = self.normal_font.render("PLEASE PAY NA KRUB", True, RED)
            thank_you_rect = thank_you.get_rect(center=(WINDOW_WIDTH // 2, 530))
            self.screen.blit(thank_you, thank_you_rect)
            
            # Restart button
            self.restart_button.draw(self.screen)
            
        except Exception as e:
            print(f"Error drawing results screen: {e}")
    
    def add_dish(self) -> None:
        """Add a dish to the list"""
        try:
            name = self.dish_name_input.text.strip()
            price_str = self.dish_price_input.text.strip()
            
            if not name:
                print("Dish name cannot be empty")
                return
            
            if name in self.dishes:
                print("Dish already exists")
                return
            
            if not price_str:
                print("Price cannot be empty")
                return
            
            try:
                price = float(price_str)
                if price < 0:
                    print("Price cannot be negative")
                    return
                
                # String encoding demonstration
                encoded_name = name.encode('utf-8')
                decoded_name = encoded_name.decode('utf-8')
                
                dish = Dish(decoded_name, price)
                self.dishes[decoded_name] = dish
                
                # Clear inputs
                self.dish_name_input.text = ""
                self.dish_price_input.text = ""
                
            except ValueError:
                print("Invalid price format")
                
        except Exception as e:
            print(f"Error adding dish: {e}")
    
    def add_person(self) -> None:
        """Add a person to the list"""
        try:
            name = self.person_name_input.text.strip()
            
            if not name:
                print("Name cannot be empty")
                return
            
            if name in self.people:
                print("Person already exists")
                return
            
            person = Person(name)
            self.people[name] = person
            
            # Clear input
            self.person_name_input.text = ""
            
        except Exception as e:
            print(f"Error adding person: {e}")
    
    def calculate_bills(self) -> None:
        """Calculate individual bills"""
        try:
            # Reset totals
            for person in self.people.values():
                person._total = 0.0
            
            # Calculate using generator
            for dish in dish_iterator(self.dishes):
                if dish.eaters:
                    shared_price = dish.get_shared_price()
                    for eater_name in dish.eaters:
                        if eater_name in self.people:
                            self.people[eater_name].add_to_total(shared_price)
                            
        except Exception as e:
            print(f"Error calculating bills: {e}")
    
    def handle_events(self) -> None:
        """Handle pygame events"""
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # State-specific event handling
                if self.state == GameState.MENU:
                    if self.start_button.handle_event(event):
                        self.state = GameState.ADD_DISHES
                
                elif self.state == GameState.ADD_DISHES:
                    self.dish_name_input.handle_event(event)
                    self.dish_price_input.handle_event(event)
                    
                    if self.add_dish_button.handle_event(event):
                        self.add_dish()
                    
                    if self.next_button.handle_event(event):
                        if len(self.dishes) > 0:
                            self.state = GameState.ADD_PEOPLE
                    
                    if self.back_button.handle_event(event):
                        self.state = GameState.MENU
                
                elif self.state == GameState.ADD_PEOPLE:
                    self.person_name_input.handle_event(event)
                    
                    if self.add_person_button.handle_event(event):
                        self.add_person()
                    
                    if self.next_button.handle_event(event):
                        if len(self.people) > 0:
                            self.state = GameState.ASSIGN_ORDERS
                            self.current_person_index = 0
                            self.selected_dishes = []
                    
                    if self.back_button.handle_event(event):
                        self.state = GameState.ADD_DISHES
                
                elif self.state == GameState.ASSIGN_ORDERS:
                    # Handle dish selection
                    if event.type == pygame.MOUSEBUTTONDOWN and hasattr(self, 'dish_rects'):
                        for dish_name, rect in self.dish_rects.items():
                            if rect.collidepoint(event.pos):
                                if dish_name in self.selected_dishes:
                                    self.selected_dishes.remove(dish_name)
                                else:
                                    self.selected_dishes.append(dish_name)
                    
                    if self.next_button.handle_event(event):
                        # Save current person's selections
                        people_list = list(self.people.values())
                        if self.current_person_index < len(people_list):
                            current_person = people_list[self.current_person_index]
                            for dish_name in self.selected_dishes:
                                if dish_name in self.dishes:
                                    self.dishes[dish_name].add_eater(current_person.name)
                        
                        # Move to next person
                        self.current_person_index += 1
                        self.selected_dishes = []
                        
                        if self.current_person_index >= len(people_list):
                            self.state = GameState.RESULTS
                            self.calculate_bills()
                    
                    if self.back_button.handle_event(event):
                        if self.current_person_index > 0:
                            self.current_person_index -= 1
                            self.selected_dishes = []
                        else:
                            self.state = GameState.ADD_PEOPLE
                
                elif self.state == GameState.RESULTS:
                    if self.restart_button.handle_event(event):
                        self.__init__()
                        
        except Exception as e:
            print(f"Error handling events: {e}")
    
    def draw(self) -> None:
        """Draw the current screen"""
        try:
            with rendering_context(self.screen):
                if self.state == GameState.MENU:
                    self.draw_menu_screen()
                elif self.state == GameState.ADD_DISHES:
                    self.draw_add_dishes_screen()
                elif self.state == GameState.ADD_PEOPLE:
                    self.draw_add_people_screen()
                elif self.state == GameState.ASSIGN_ORDERS:
                    self.draw_assign_orders_screen()
                elif self.state == GameState.RESULTS:
                    self.draw_results_screen()
        except Exception as e:
            print(f"Error in draw: {e}")
    
    def run(self) -> None:
        """Main game loop"""
        try:
            while self.running:
                self.handle_events()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"Error in main loop: {e}")
        finally:
            pygame.quit()
            sys.exit()


def main():
    """Entry point of the application"""
    try:
        app = BillSplitterApp()
        app.run()
    except Exception as e:
        print(f"Application error: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()