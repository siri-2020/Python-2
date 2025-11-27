import pygame
import sys
import urllib.request
import os

# --------------------------------------------------
#  BILL SPLITTER – Thai Language + Language Selection
# --------------------------------------------------
#  Features:
#    ✔ Language selection screen with flag emojis
#    ✔ Downloads Thai font automatically
#    ✔ Works in VSCode terminal
#    ✔ Enter key to add, Tab to switch fields
# --------------------------------------------------

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
LIGHT_GRAY = (240, 240, 240)
BLUE = (120, 160, 255)
BLUE_HOVER = (90, 130, 225)
GREEN = (140, 230, 140)
GREEN_HOVER = (110, 200, 110)
RED = (240, 130, 130)
RED_HOVER = (210, 100, 100)
ORANGE = (255, 180, 100)

# Download Thai font if not exists
def download_thai_font():
    """Download Sarabun Thai font from Google Fonts"""
    font_dir = "fonts"
    font_file = os.path.join(font_dir, "Sarabun-Regular.ttf")
    
    if not os.path.exists(font_dir):
        os.makedirs(font_dir)
    
    if not os.path.exists(font_file):
        print("Downloading Thai font...")
        try:
            url = "https://github.com/cadsondemak/Sarabun/raw/master/fonts/ttf/Sarabun-Regular.ttf"
            urllib.request.urlretrieve(url, font_file)
            print("Font downloaded successfully!")
        except Exception as e:
            print(f"Warning: Could not download font: {e}")
            return None
    
    return font_file

# Try to get Thai font
THAI_FONT_PATH = download_thai_font()

# Initialize fonts
def get_font(size):
    if THAI_FONT_PATH and os.path.exists(THAI_FONT_PATH):
        return pygame.font.Font(THAI_FONT_PATH, size)
    else:
        # Fallback to system font
        try:
            return pygame.font.SysFont('tahoma,leelawadee,arial', size)
        except:
            return pygame.font.Font(None, size)

FONT = get_font(28)
SMALL_FONT = get_font(24)
BIG = get_font(48)
HUGE = get_font(72)

SCREEN = pygame.display.set_mode((1000, 700))
pygame.display.set_caption("Bill Splitter – ตัวแบ่งบิล")

pygame.key.set_text_input_rect(pygame.Rect(0, 0, 800, 600))

# Language texts
TEXTS = {
    'en': {
        'title': 'Bill Splitter',
        'step1': 'Step 1: Add Dishes',
        'step2': 'Step 2: Add People',
        'step3': 'Step 3: Who Ate What?',
        'step4': 'Step 4: Final Bill',
        'dish_placeholder': 'Dish name...',
        'price_placeholder': 'Price',
        'person_placeholder': 'Person name...',
        'add': 'Add',
        'delete': 'Delete',
        'next': 'Next →',
        'back': '← Back',
        'start_over': 'Start Over',
        'no_dishes': 'No dishes added yet',
        'no_people': 'No people added yet',
        'instruction1': 'Press TAB to switch, ENTER to add',
        'instruction2': 'Press ENTER to add',
        'instruction3': 'Click names to select (green = ate it)',
        'dishes': 'Dishes:',
        'each_pays': 'Each Person Pays:',
        'total': 'Total Bill:',
        'nobody': 'Nobody',
        'err_dish_name': 'Please enter a dish name!',
        'err_price': 'Please enter a price!',
        'err_price_positive': 'Price must be positive!',
        'err_price_format': 'Invalid price format!',
        'err_person_name': 'Please enter a name!',
        'err_person_exists': 'Person already added!',
        'select_language': 'Select Language',
    },
    'th': {
        'title': 'ตัวแบ่งบิล',
        'step1': 'ขั้นตอนที่ 1: เพิ่มรายการอาหาร',
        'step2': 'ขั้นตอนที่ 2: เพิ่มรายชื่อคน',
        'step3': 'ขั้นตอนที่ 3: ใครกินอะไร?',
        'step4': 'ขั้นตอนที่ 4: สรุปบิล',
        'dish_placeholder': 'ชื่ออาหาร...',
        'price_placeholder': 'ราคา',
        'person_placeholder': 'ชื่อคน...',
        'add': 'เพิ่ม',
        'delete': 'ลบ',
        'next': 'ถัดไป →',
        'back': '← กลับ',
        'start_over': 'เริ่มใหม่',
        'no_dishes': 'ยังไม่มีรายการอาหาร',
        'no_people': 'ยังไม่มีรายชื่อ',
        'instruction1': 'กด TAB สลับช่อง, ENTER เพิ่ม',
        'instruction2': 'กด ENTER เพื่อเพิ่ม',
        'instruction3': 'คลิกชื่อเพื่อเลือก (เขียว = กิน)',
        'dishes': 'รายการอาหาร:',
        'each_pays': 'แต่ละคนจ่าย:',
        'total': 'รวมทั้งหมด:',
        'nobody': 'ไม่มีใครกิน',
        'err_dish_name': 'กรุณากรอกชื่ออาหาร!',
        'err_price': 'กรุณากรอกราคา!',
        'err_price_positive': 'ราคาต้องมากกว่า 0!',
        'err_price_format': 'รูปแบบราคาไม่ถูกต้อง!',
        'err_person_name': 'กรุณากรอกชื่อ!',
        'err_person_exists': 'มีชื่อนี้แล้ว!',
        'select_language': 'เลือกภาษา',
    }
}

# --------------------------------------------------
#  BUTTON CLASS
# --------------------------------------------------
class Button:
    def __init__(self, x, y, w, h, text, color=BLUE, hover_color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color or color
        self.is_hovered = False

    def draw(self, surf):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surf, color, self.rect, border_radius=5)
        pygame.draw.rect(surf, BLACK, self.rect, 2, border_radius=5)
        txt = FONT.render(self.text, True, BLACK)
        txt_rect = txt.get_rect(center=self.rect.center)
        surf.blit(txt, txt_rect)

    def update(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)

# --------------------------------------------------
#  INPUT BOX CLASS
# --------------------------------------------------
class InputBox:
    def __init__(self, x, y, w, h, placeholder="", number_only=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ""
        self.active = False
        self.placeholder = placeholder
        self.number_only = number_only

    def draw(self, surf):
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(surf, color, self.rect, border_radius=3)
        
        border_color = BLUE if self.active else GRAY
        border_width = 3 if self.active else 2
        pygame.draw.rect(surf, border_color, self.rect, border_width, border_radius=3)
        
        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else GRAY
        
        txt = FONT.render(display_text, True, text_color)
        
        max_width = self.rect.width - 16
        if txt.get_width() > max_width:
            visible_text = display_text
            while len(visible_text) > 0:
                txt = FONT.render(visible_text, True, text_color)
                if txt.get_width() <= max_width:
                    break
                visible_text = visible_text[1:]
        
        surf.blit(txt, (self.rect.x + 8, self.rect.y + 8))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
                return None
            elif event.key == pygame.K_RETURN:
                return "ENTER"
            elif event.key == pygame.K_TAB:
                return "TAB"
            
        if event.type == pygame.TEXTINPUT and self.active:
            if self.number_only:
                if event.text.isdigit() or event.text == '.':
                    if len(self.text) < 40:
                        self.text += event.text
            else:
                if len(self.text) < 40:
                    self.text += event.text
                    
        return None

    def activate(self):
        self.active = True
    
    def deactivate(self):
        self.active = False

# --------------------------------------------------
#  MAIN APPLICATION
# --------------------------------------------------
class BillApp:
    def __init__(self):
        self.step = 0  # 0=language, 1=dishes, 2=people, 3=select, 4=result
        self.language = None  # 'en' or 'th'
        
        self.menu = {}
        self.people = []
        self.eaters = {}
        
        self.dish_name_box = None
        self.price_box = None
        self.person_name_box = None
        
        self.error_msg = ""
        self.error_timer = 0

    def t(self, key):
        """Get translated text"""
        if self.language and key in TEXTS[self.language]:
            return TEXTS[self.language][key]
        return key

    def show_error(self, msg):
        self.error_msg = msg
        self.error_timer = 90

    def init_input_boxes(self):
        """Initialize input boxes with correct placeholders"""
        self.dish_name_box = InputBox(50, 520, 350, 45, self.t('dish_placeholder'))
        self.price_box = InputBox(420, 520, 200, 45, self.t('price_placeholder'), number_only=True)
        self.person_name_box = InputBox(50, 520, 450, 45, self.t('person_placeholder'))
        self.dish_name_box.activate()

    def add_dish(self):
        dish_name = self.dish_name_box.text.strip()
        price_text = self.price_box.text.strip()
        
        if not dish_name:
            self.show_error(self.t('err_dish_name'))
        elif not price_text:
            self.show_error(self.t('err_price'))
        else:
            try:
                price = float(price_text)
                if price > 0:
                    self.menu[dish_name] = price
                    self.dish_name_box.text = ""
                    self.price_box.text = ""
                    self.dish_name_box.activate()
                    self.price_box.deactivate()
                else:
                    self.show_error(self.t('err_price_positive'))
            except ValueError:
                self.show_error(self.t('err_price_format'))

    def add_person(self):
        name = self.person_name_box.text.strip()
        
        if not name:
            self.show_error(self.t('err_person_name'))
        elif name in self.people:
            self.show_error(self.t('err_person_exists'))
        else:
            self.people.append(name)
            self.person_name_box.text = ""

    # -------------------- STEP 0: LANGUAGE SELECTION --------------------
    def draw_language_select(self):
        SCREEN.fill(GRAY)
        
        # Title
        title = HUGE.render("Bill Splitter", True, BLACK)
        title_rect = title.get_rect(center=(500, 150))
        SCREEN.blit(title, title_rect)
        
        subtitle = BIG.render("ตัวแบ่งบิล", True, BLACK)
        subtitle_rect = subtitle.get_rect(center=(500, 220))
        SCREEN.blit(subtitle, subtitle_rect)
        
        # Language selection text
        select = FONT.render("Select Language / เลือกภาษา", True, BLACK)
        select_rect = select.get_rect(center=(500, 300))
        SCREEN.blit(select, select_rect)
        
        # Language buttons with flags (using text)
        en_btn = Button(250, 380, 200, 100, "🇬🇧 English", BLUE, BLUE_HOVER)
        th_btn = Button(550, 380, 200, 100, "🇹🇭 ไทย", GREEN, GREEN_HOVER)
        
        en_btn.update(pygame.mouse.get_pos())
        th_btn.update(pygame.mouse.get_pos())
        
        en_btn.draw(SCREEN)
        th_btn.draw(SCREEN)
        
        self.buttons = [en_btn, th_btn]
        
        pygame.display.flip()

    # -------------------- STEP 1: ADD DISHES --------------------
    def draw_step1(self):
        SCREEN.fill(GRAY)
        
        title = BIG.render(self.t('step1'), True, BLACK)
        SCREEN.blit(title, (50, 30))
        
        progress = SMALL_FONT.render("Step 1 of 4", True, BLACK)
        SCREEN.blit(progress, (820, 40))
        
        y = 100
        if not self.menu:
            txt = SMALL_FONT.render(self.t('no_dishes'), True, GRAY)
            SCREEN.blit(txt, (70, y))
        else:
            for dish, price in self.menu.items():
                txt = FONT.render(f"• {dish} - ฿{price:.2f}", True, BLACK)
                SCREEN.blit(txt, (70, y))
                
                del_btn = Button(750, y, 100, 30, self.t('delete'), RED, RED_HOVER)
                del_btn.update(pygame.mouse.get_pos())
                del_btn.draw(SCREEN)
                if not hasattr(self, 'del_buttons'):
                    self.del_buttons = []
                self.del_buttons.append((dish, del_btn))
                
                y += 40
        
        inst = SMALL_FONT.render(self.t('instruction1'), True, BLACK)
        SCREEN.blit(inst, (50, 470))
        
        self.dish_name_box.draw(SCREEN)
        self.price_box.draw(SCREEN)
        
        add_btn = Button(640, 520, 100, 45, self.t('add'), GREEN, GREEN_HOVER)
        next_btn = Button(820, 630, 150, 50, self.t('next'), GREEN, GREEN_HOVER)
        
        add_btn.update(pygame.mouse.get_pos())
        next_btn.update(pygame.mouse.get_pos())
        
        add_btn.draw(SCREEN)
        if self.menu:
            next_btn.draw(SCREEN)
        
        self.buttons = [add_btn, next_btn]
        
        self.draw_error()
        pygame.display.flip()

    # -------------------- STEP 2: ADD PEOPLE --------------------
    def draw_step2(self):
        SCREEN.fill(GRAY)
        
        title = BIG.render(self.t('step2'), True, BLACK)
        SCREEN.blit(title, (50, 30))
        
        progress = SMALL_FONT.render("Step 2 of 4", True, BLACK)
        SCREEN.blit(progress, (820, 40))
        
        y = 100
        if not self.people:
            txt = SMALL_FONT.render(self.t('no_people'), True, GRAY)
            SCREEN.blit(txt, (70, y))
        else:
            self.del_buttons = []
            for person in self.people:
                txt = FONT.render(f"• {person}", True, BLACK)
                SCREEN.blit(txt, (70, y))
                
                del_btn = Button(750, y, 100, 30, self.t('delete'), RED, RED_HOVER)
                del_btn.update(pygame.mouse.get_pos())
                del_btn.draw(SCREEN)
                self.del_buttons.append((person, del_btn))
                
                y += 40
        
        inst = SMALL_FONT.render(self.t('instruction2'), True, BLACK)
        SCREEN.blit(inst, (50, 470))
        
        self.person_name_box.draw(SCREEN)
        
        add_btn = Button(520, 520, 100, 45, self.t('add'), GREEN, GREEN_HOVER)
        back_btn = Button(50, 630, 150, 50, self.t('back'), ORANGE, RED_HOVER)
        next_btn = Button(820, 630, 150, 50, self.t('next'), GREEN, GREEN_HOVER)
        
        add_btn.update(pygame.mouse.get_pos())
        back_btn.update(pygame.mouse.get_pos())
        next_btn.update(pygame.mouse.get_pos())
        
        add_btn.draw(SCREEN)
        back_btn.draw(SCREEN)
        if self.people:
            next_btn.draw(SCREEN)
        
        self.buttons = [add_btn, back_btn, next_btn]
        
        self.draw_error()
        pygame.display.flip()

    # -------------------- STEP 3: SELECT WHO ATE WHAT --------------------
    def draw_step3(self):
        SCREEN.fill(GRAY)
        
        title = BIG.render(self.t('step3'), True, BLACK)
        SCREEN.blit(title, (50, 30))
        
        progress = SMALL_FONT.render("Step 3 of 4", True, BLACK)
        SCREEN.blit(progress, (820, 40))
        
        subtitle = SMALL_FONT.render(self.t('instruction3'), True, BLACK)
        SCREEN.blit(subtitle, (50, 80))
        
        y = 130
        self.person_buttons = []
        
        for dish in self.menu.keys():
            dish_txt = FONT.render(f"{dish}:", True, BLACK)
            SCREEN.blit(dish_txt, (50, y))
            
            x = 280
            if dish not in self.eaters:
                self.eaters[dish] = []
            
            for person in self.people:
                is_selected = person in self.eaters[dish]
                color = GREEN if is_selected else RED
                hover_color = GREEN_HOVER if is_selected else RED_HOVER
                
                btn = Button(x, y, 140, 35, person, color, hover_color)
                btn.update(pygame.mouse.get_pos())
                btn.draw(SCREEN)
                self.person_buttons.append((dish, person, btn))
                
                x += 150
            
            y += 50
        
        back_btn = Button(50, 630, 150, 50, self.t('back'), ORANGE, RED_HOVER)
        next_btn = Button(820, 630, 150, 50, self.t('next'), GREEN, GREEN_HOVER)
        
        back_btn.update(pygame.mouse.get_pos())
        next_btn.update(pygame.mouse.get_pos())
        
        back_btn.draw(SCREEN)
        next_btn.draw(SCREEN)
        
        self.buttons = [back_btn, next_btn]
        
        self.draw_error()
        pygame.display.flip()

    # -------------------- STEP 4: RESULT --------------------
    def draw_step4(self):
        SCREEN.fill(GRAY)
        
        title = BIG.render(self.t('step4'), True, BLACK)
        SCREEN.blit(title, (50, 30))
        
        progress = SMALL_FONT.render("Step 4 of 4", True, BLACK)
        SCREEN.blit(progress, (820, 40))
        
        totals = {p: 0 for p in self.people}
        grand_total = sum(self.menu.values())
        
        y = 100
        subtitle = FONT.render(self.t('dishes'), True, BLACK)
        SCREEN.blit(subtitle, (50, y))
        y += 40
        
        for dish, price in self.menu.items():
            eaters = self.eaters.get(dish, [])
            eaters_str = ", ".join(eaters) if eaters else self.t('nobody')
            
            txt = SMALL_FONT.render(f"• {dish}: ฿{price:.2f} ({eaters_str})", True, BLACK)
            SCREEN.blit(txt, (70, y))
            
            if eaters:
                share = price / len(eaters)
                for p in eaters:
                    totals[p] += share
            
            y += 30
        
        y += 30
        subtitle = FONT.render(self.t('each_pays'), True, BLACK)
        SCREEN.blit(subtitle, (50, y))
        y += 40
        
        for person, amount in totals.items():
            txt = FONT.render(f"• {person}: ฿{amount:.2f}", True, BLACK)
            SCREEN.blit(txt, (70, y))
            y += 35
        
        y += 20
        total_txt = BIG.render(f"{self.t('total')} ฿{grand_total:.2f}", True, BLACK)
        SCREEN.blit(total_txt, (50, y))
        
        back_btn = Button(50, 630, 150, 50, self.t('back'), ORANGE, RED_HOVER)
        restart_btn = Button(400, 630, 200, 50, self.t('start_over'), BLUE, BLUE_HOVER)
        
        back_btn.update(pygame.mouse.get_pos())
        restart_btn.update(pygame.mouse.get_pos())
        
        back_btn.draw(SCREEN)
        restart_btn.draw(SCREEN)
        
        self.buttons = [back_btn, restart_btn]
        
        pygame.display.flip()

    def draw_error(self):
        if self.error_timer > 0:
            txt = SMALL_FONT.render(self.error_msg, True, RED)
            SCREEN.blit(txt, (50, 580))
            self.error_timer -= 1

    # -------------------- UPDATE LOGIC --------------------
    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            # STEP 0: Language Selection
            if self.step == 0:
                if self.buttons[0].clicked((mx, my)):  # English
                    self.language = 'en'
                    self.step = 1
                    self.init_input_boxes()
                elif self.buttons[1].clicked((mx, my)):  # Thai
                    self.language = 'th'
                    self.step = 1
                    self.init_input_boxes()

            # STEP 1: Add Dishes
            elif self.step == 1:
                self.del_buttons = []
                
                if self.buttons[0].clicked((mx, my)):
                    self.add_dish()
                
                elif len(self.buttons) > 1 and self.buttons[1].clicked((mx, my)):
                    if self.menu:
                        self.step = 2
                        self.dish_name_box.deactivate()
                        self.price_box.deactivate()
                        self.person_name_box.activate()
                
                y = 100
                for dish in list(self.menu.keys()):
                    del_rect = pygame.Rect(750, y, 100, 30)
                    if del_rect.collidepoint((mx, my)):
                        del self.menu[dish]
                        if dish in self.eaters:
                            del self.eaters[dish]
                        break
                    y += 40

            # STEP 2: Add People
            elif self.step == 2:
                if self.buttons[0].clicked((mx, my)):
                    self.add_person()
                
                elif self.buttons[1].clicked((mx, my)):
                    self.step = 1
                    self.person_name_box.deactivate()
                    self.dish_name_box.activate()
                
                elif len(self.buttons) > 2 and self.buttons[2].clicked((mx, my)):
                    if self.people:
                        self.step = 3
                        self.person_name_box.deactivate()
                
                if hasattr(self, 'del_buttons'):
                    for person, btn in self.del_buttons:
                        if btn.clicked((mx, my)):
                            self.people.remove(person)
                            for dish in self.eaters:
                                if person in self.eaters[dish]:
                                    self.eaters[dish].remove(person)

            # STEP 3: Select
            elif self.step == 3:
                if hasattr(self, 'person_buttons'):
                    for dish, person, btn in self.person_buttons:
                        if btn.clicked((mx, my)):
                            if person in self.eaters[dish]:
                                self.eaters[dish].remove(person)
                            else:
                                self.eaters[dish].append(person)
                
                if self.buttons[0].clicked((mx, my)):
                    self.step = 2
                    self.person_name_box.activate()
                
                elif self.buttons[1].clicked((mx, my)):
                    self.step = 4

            # STEP 4: Result
            elif self.step == 4:
                if self.buttons[0].clicked((mx, my)):
                    self.step = 3
                
                elif self.buttons[1].clicked((mx, my)):
                    self.step = 0
                    self.language = None
                    self.menu = {}
                    self.people = []
                    self.eaters = {}

        # Handle input boxes
        if self.step == 1 and self.dish_name_box:
            result1 = self.dish_name_box.handle(event)
            result2 = self.price_box.handle(event)
            
            if result1 == "TAB":
                self.dish_name_box.deactivate()
                self.price_box.activate()
            elif result2 == "TAB":
                self.price_box.deactivate()
                self.dish_name_box.activate()
            
            if result1 == "ENTER" or result2 == "ENTER":
                self.add_dish()
                
        elif self.step == 2 and self.person_name_box:
            result = self.person_name_box.handle(event)
            
            if result == "ENTER":
                self.add_person()

    # -------------------- MAIN DRAW ROUTER --------------------
    def draw(self):
        if self.step == 0:
            self.draw_language_select()
        elif self.step == 1:
            self.draw_step1()
        elif self.step == 2:
            self.draw_step2()
        elif self.step == 3:
            self.draw_step3()
        elif self.step == 4:
            self.draw_step4()

# --------------------------------------------------
#  MAIN LOOP
# --------------------------------------------------
def main():
    app = BillApp()
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            app.update(event)

        app.draw()
        clock.tick(30)

if __name__ == "__main__":
    main()