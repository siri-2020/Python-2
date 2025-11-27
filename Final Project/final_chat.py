import pygame
import sys
import datetime
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
    MENU = 0
    ADD_DISHES = 1
    ADD_PEOPLE = 2
    ASSIGN_ORDERS = 3
    RESULTS = 4


def safe_draw(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            print(f"Drawing error in {func.__name__}: {e}")
    return wrapper


class UIComponent(ABC):
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = True

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        pass

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        pass


class Button(UIComponent):
    def __init__(self, x, y, w, h, text, color=BLUE, text_color=WHITE):
        super().__init__(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = LIGHT_BLUE
        self.text_color = text_color
        self.hovered = False
        self.font = pygame.font.Font(None, 32)

    @safe_draw
    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class InputBox(UIComponent):
    def __init__(self, x, y, w, h, placeholder="", numeric_only=False):
        super().__init__(x, y, w, h)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.numeric_only = numeric_only
        self.font = pygame.font.Font(None, 32)
        self.color_inactive = GRAY
        self.color_active = BLUE

    @safe_draw
    def draw(self, surface):
        color = self.color_active if self.active else self.color_inactive
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=5)

        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else DARK_GRAY

        text_surface = self.font.render(display_text, True, text_color)
        surface.blit(text_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
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


@contextmanager
def rendering_context(surface: pygame.Surface, color=WHITE):
    try:
        surface.fill(color)
        yield surface
        pygame.display.flip()
    except Exception as e:
        print(f"Rendering error: {e}")
        raise


class MenuItem(ABC):
    def __init__(self, name, price):
        self._name = name
        self._price = price

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @abstractmethod
    def get_info(self):
        pass


class Dish(MenuItem):
    def __init__(self, name, price):
        super().__init__(name, price)
        self._eaters: List[str] = []

    @property
    def eaters(self):
        return self._eaters

    def add_eater(self, person_name):
        if person_name not in self._eaters:
            self._eaters.append(person_name)

    def get_shared_price(self):
        if len(self._eaters) == 0:
            return 0.0
        return self._price / len(self._eaters)

    def get_info(self):
        return f"{self.name}: THB {self.price:.2f}"


class Person:
    def __init__(self, name):
        self._name = name.strip()
        self._total = 0.0

    @property
    def name(self):
        return self._name

    @property
    def total(self):
        return self._total

    def add_to_total(self, amount):
        self._total += amount


def dish_iterator(dishes):
    for dish in dishes.values():
        yield dish


class BillSplitterApp:
    def __init__(self):
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
        self.dishes = {}
        self.people = {}
        self.current_person_index = 0
        self.selected_dishes = []

        self.state = GameState.MENU
        self.scroll_offset = 0

        self.setup_ui()

    def setup_ui(self):
        self.dish_name_input = InputBox(50, 200, 350, 50, "Dish name...")
        self.dish_price_input = InputBox(450, 200, 250, 50, "Price (THB)...", numeric_only=True)
        self.person_name_input = InputBox(50, 200, 600, 50, "Person name...")

        self.start_button = Button(300, 300, 300, 60, "Start Bill Split", GREEN)
        self.add_dish_button = Button(720, 200, 150, 50, "Add Dish", GREEN)
        self.next_button = Button(650, 600, 200, 60, "Next", BLUE)
        self.back_button = Button(50, 600, 200, 60, "Back", GRAY)
        self.add_person_button = Button(670, 200, 200, 50, "Add Person", GREEN)
        self.calculate_button = Button(300, 600, 300, 60, "Calculate Bills", GREEN)
        self.restart_button = Button(300, 600, 300, 60, "Start Over", BLUE)

    ### Print ###
    def save_results_to_file(self):
    """Save bill summary with timestamp in unique file."""
    try:
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"bill_{now}.txt"

        with open(filename, "w", encoding="utf-8") as f:
            f.write("===== Bill Summary =====\n")
            f.write(f"Generated at: {now}\n\n")

            for person in self.people.values():
                f.write(f"{person.name}: THB {person.total:.2f}\n")

            total_bill = sum(dish.price for dish in self.dishes.values())
            f.write(f"\nTotal Bill: THB {total_bill:.2f}\n")
            f.write("=========================\n\n")

        print(f"Bill saved to {filename}")

    except Exception as e:
        print(f"Error saving bill: {e}")

    @safe_draw
    def draw_menu_screen(self):
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
            "3. Assign who ate what",
            "4. Get results!"
        ]
        y = 400
        for t in instructions:
            text = self.normal_font.render(t, True, BLACK)
            rect = text.get_rect(center=(WINDOW_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 40

    @safe_draw
    def draw_add_dishes_screen(self):
        header = self.header_font.render("Add Dishes", True, BLUE)
        self.screen.blit(header, (50, 50))

        instruction = self.small_font.render("Enter dish name & price", True, DARK_GRAY)
        self.screen.blit(instruction, (50, 120))

        self.dish_name_input.draw(self.screen)
        self.dish_price_input.draw(self.screen)
        self.add_dish_button.draw(self.screen)

        y = 280
        dishes_header = self.normal_font.render(f"Dishes ({len(self.dishes)}):", True, BLACK)
        self.screen.blit(dishes_header, (50, y))

        y += 50
        for dish in list(self.dishes.values())[:8]:
            dish_text = self.small_font.render(f"• {dish.get_info()}", True, BLACK)
            self.screen.blit(dish_text, (70, y))
            y += 35

        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def draw_add_people_screen(self):
        header = self.header_font.render("Add People", True, BLUE)
        self.screen.blit(header, (50, 50))

        instruction = self.small_font.render("Enter each person's name", True, DARK_GRAY)
        self.screen.blit(instruction, (50, 120))

        self.person_name_input.draw(self.screen)
        self.add_person_button.draw(self.screen)

        y = 280
        p_header = self.normal_font.render(f"People ({len(self.people)}):", True, BLACK)
        self.screen.blit(p_header, (50, y))

        y += 50
        for p in list(self.people.values())[:10]:
            txt = self.small_font.render(f"• {p.name}", True, BLACK)
            self.screen.blit(txt, (70, y))
            y += 35

        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def draw_assign_orders_screen(self):
        if not self.people:
            return

        people_list = list(self.people.values())
        if self.current_person_index >= len(people_list):
            self.state = GameState.RESULTS
            self.calculate_bills()

            ### ADDED ###
            self.save_results_to_file()

            return

        current_person = people_list[self.current_person_index]

        header = self.header_font.render(f"What did {current_person.name} eat?", True, BLUE)
        self.screen.blit(header, (50, 50))

        y = 170
        self.dish_rects = {}

        for dish in list(self.dishes.values()):
            rect = pygame.Rect(50, y, 800, 40)
            self.dish_rects[dish.name] = rect

            is_selected = dish.name in self.selected_dishes
            color = LIGHT_BLUE if is_selected else LIGHT_GRAY

            pygame.draw.rect(self.screen, color, rect, border_radius=5)
            pygame.draw.rect(self.screen, DARK_GRAY, rect, 2, border_radius=5)

            text = self.normal_font.render(
                ("✓ " if is_selected else "  ") + dish.get_info(), True, BLACK
            )
            self.screen.blit(text, (60, y + 5))

            y += 50

        self.next_button.text = (
            "Next Person" if self.current_person_index < len(self.people) - 1 else "Finish"
        )
        self.next_button.draw(self.screen)
        self.back_button.draw(self.screen)

    @safe_draw
    def draw_results_screen(self):
        header = self.header_font.render("Bill Summary", True, GREEN)
        self.screen.blit(header, (50, 30))

        y = 100

        for person in self.people.values():
            txt = self.normal_font.render(
                f"{person.name}: THB {person.total:.2f}", True, BLACK
            )
            self.screen.blit(txt, (50, y))
            y += 45

        total_bill = sum(dish.price for dish in self.dishes.values())
        y += 20

        pygame.draw.line(self.screen, DARK_GRAY, (50, y), (WINDOW_WIDTH - 50, y), 2)
        y += 30

        total_txt = self.header_font.render(f"Total: THB {total_bill:.2f}", True, BLUE)
        self.screen.blit(total_txt, (50, y))

        thank = self.normal_font.render("PLEASE PAY NA KRUB", True, RED)
        thank_rect = thank.get_rect(center=(WINDOW_WIDTH // 2, 530))
        self.screen.blit(thank, thank_rect)

        self.restart_button.draw(self.screen)

    def add_dish(self):
        name = self.dish_name_input.text.strip()
        price_str = self.dish_price_input.text.strip()

        if not name or not price_str:
            return

        if name in self.dishes:
            return

        try:
            price = float(price_str)
        except:
            return

        dish = Dish(name, price)
        self.dishes[name] = dish

        self.dish_name_input.text = ""
        self.dish_price_input.text = ""

    def add_person(self):
        name = self.person_name_input.text.strip()
        if not name or name in self.people:
            return

        self.people[name] = Person(name)
        self.person_name_input.text = ""

    def calculate_bills(self):
        for person in self.people.values():
            person._total = 0.0

        for dish in dish_iterator(self.dishes):
            shared = dish.get_shared_price()
            for eater in dish.eaters:
                if eater in self.people:
                    self.people[eater].add_to_total(shared)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.state == GameState.MENU:
                if self.start_button.handle_event(event):
                    self.state = GameState.ADD_DISHES

            elif self.state == GameState.ADD_DISHES:
                self.dish_name_input.handle_event(event)
                self.dish_price_input.handle_event(event)

                if self.add_dish_button.handle_event(event):
                    self.add_dish()

                if self.next_button.handle_event(event):
                    if self.dishes:
                        self.state = GameState.ADD_PEOPLE

                if self.back_button.handle_event(event):
                    self.state = GameState.MENU

            elif self.state == GameState.ADD_PEOPLE:
                self.person_name_input.handle_event(event)

                if self.add_person_button.handle_event(event):
                    self.add_person()

                if self.next_button.handle_event(event) and self.people:
                    self.state = GameState.ASSIGN_ORDERS
                    self.current_person_index = 0
                    self.selected_dishes = []

                if self.back_button.handle_event(event):
                    self.state = GameState.ADD_DISHES

            elif self.state == GameState.ASSIGN_ORDERS:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for dname, rect in self.dish_rects.items():
                        if rect.collidepoint(event.pos):
                            if dname in self.selected_dishes:
                                self.selected_dishes.remove(dname)
                            else:
                                self.selected_dishes.append(dname)

                if self.next_button.handle_event(event):
                    people_list = list(self.people.values())

                    if self.current_person_index < len(people_list):
                        person = people_list[self.current_person_index]
                        for d in self.selected_dishes:
                            self.dishes[d].add_eater(person.name)

                    self.current_person_index += 1
                    self.selected_dishes = []

                    if self.current_person_index >= len(people_list):
                        self.state = GameState.RESULTS
                        self.calculate_bills()
                        self.save_results_to_file()  ### ADDED

                if self.back_button.handle_event(event):
                    if self.current_person_index > 0:
                        self.current_person_index -= 1
                        self.selected_dishes = []
                    else:
                        self.state = GameState.ADD_PEOPLE

            elif self.state == GameState.RESULTS:
                if self.restart_button.handle_event(event):
                    self.__init__()

    def draw(self):
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

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()


def main():
    app = BillSplitterApp()
    app.run()


if __name__ == "__main__":
    main()
