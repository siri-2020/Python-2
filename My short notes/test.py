import pygame
import sys

# ---------------------------
# 1. ตั้งค่าเริ่มต้น Pygame
# ---------------------------
pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Complete Example")

clock = pygame.time.Clock()
FPS = 60

# ---------------------------
# 2. โหลดรูปภาพ / เสียง
# ---------------------------
player_img = pygame.Surface((50, 50))
player_img.fill((0, 150, 255))   # สร้างสี่เหลี่ยมสีฟ้าแทนรูปผู้เล่น

enemy_img = pygame.Surface((40, 40))
enemy_img.fill((255, 80, 80))    # สร้างสี่เหลี่ยมสีแดงแทนศัตรู

# (ถ้าต้องการใช้ไฟล์จริง uncomment)
# player_img = pygame.image.load("player.png").convert_alpha()

# เสียง (ต้องมีไฟล์จริง)
# hit_sound = pygame.mixer.Sound("hit.wav")

# ---------------------------
# 3. วัตถุในเกม
# ---------------------------
player = pygame.Rect(400, 300, 50, 50)
enemy = pygame.Rect(100, 100, 40, 40)

player_speed = 5
enemy_speed = 3

# ---------------------------
# 4. ฟอนต์สำหรับข้อความ
# ---------------------------
font = pygame.font.SysFont("Arial", 28)


# ---------------------------
# 5. loop หลักของเกม
# ---------------------------
while True:

    # -----------------------
    # 5.1 EVENT HANDLING
    # -----------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # -----------------------
    # 5.2 INPUT KEYBOARD
    # -----------------------
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.x -= player_speed
    if keys[pygame.K_RIGHT]:
        player.x += player_speed
    if keys[pygame.K_UP]:
        player.y -= player_speed
    if keys[pygame.K_DOWN]:
        player.y += player_speed

    # -----------------------
    # 5.3 LOGIC / MOVEMENT
    # -----------------------
    enemy.x += enemy_speed
    if enemy.right > WIDTH or enemy.left < 0:
        enemy_speed = -enemy_speed

    # -----------------------
    # 5.4 COLLISION DETECTION
    # -----------------------
    if player.colliderect(enemy):
        # hit_sound.play()   # ถ้ามีเสียง
        player.x, player.y = 400, 300   # รีเซ็ตตำแหน่ง
        print("Hit!")

    # -----------------------
    # 5.5 DRAWING / RENDERING
    # -----------------------
    screen.fill((30, 30, 30))  # ทำความสะอาดหน้าจอ

    # วาดวัตถุ
    screen.blit(player_img, player)
    screen.blit(enemy_img, enemy)

    # วาดรูปเพิ่ม (วงกลม สี่เหลี่ยม เส้น)
    pygame.draw.circle(screen, (255, 255, 0), (100, 500), 30)
    pygame.draw.rect(screen, (0, 255, 100), (200, 450, 120, 60))
    pygame.draw.line(screen, (200, 200, 255), (0, 0), (800, 600), 3)

    # -----------------------
    # 5.6 DRAW TEXT
    # -----------------------
    text = font.render("Arrow keys to move. Avoid the red box!", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    # อัปเดตหน้าจอ
    pygame.display.flip()

    # -----------------------
    # 5.7 ควบคุม FPS
    # -----------------------
    clock.tick(FPS)
