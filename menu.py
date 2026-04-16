import pygame
import os

#Menu settings
SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 900

BG_COLOR = (49, 96, 160)
NAVY = (8, 28, 92)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 224, 77)
DARK_BLUE = (18, 41, 107)
ORANGE = (255, 155, 70)
SHADOW = (20, 45, 90)
LOCK_OVERLAY = (0, 0, 0, 125)

PLAYER_COLORS = [
    ("Blue", (0, 80, 255)),
    ("Red", (255, 70, 50)),
    ("Green", (60, 200, 90)),
    ("Yellow", (245, 220, 60)),
    ("Purple", (160, 90, 220)),
    ("Orange", (255, 145, 40)),
    ("Pink", (255, 105, 180)),
    ("Cyan", (0, 200, 255)),
]

MAPS = [
    {"name": "Greenwood Village", "image": "Map1.png"},
    {"name": "Meadow Crossing", "image": "Map2.png"},
    {"name": "The Underkeep", "image": "Map3.png"},
]

# Only The Underkeep is unlocked
UNLOCKED_MAPS = [False, False, True]

#Helper functions
def draw_text(screen, text, font, color, center=None, topleft=None):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = center
    elif topleft:
        rect.topleft = topleft
    screen.blit(surf, rect)
    return rect


def draw_rounded_panel(screen, rect, color, border_color=None, border_width=0, radius=20):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    if border_color and border_width > 0:
        pygame.draw.rect(screen, border_color, rect, width=border_width, border_radius=radius)


def draw_arrow_button(screen, rect, direction="left"):
    draw_rounded_panel(screen, rect, ORANGE, border_color=(180, 100, 30), border_width=3, radius=14)
    cx, cy = rect.center
    if direction == "left":
        points = [(cx + 8, cy - 12), (cx - 8, cy), (cx + 8, cy + 12)]
    else:
        points = [(cx - 8, cy - 12), (cx + 8, cy), (cx - 8, cy + 12)]
    pygame.draw.polygon(screen, WHITE, points)


def load_image_keep_ratio(path, max_size):
    if not path or not os.path.exists(path):
        return None

    img = pygame.image.load(path).convert()
    iw, ih = img.get_size()
    mw, mh = max_size

    scale = min(mw / iw, mh / ih)
    new_w = max(1, int(iw * scale))
    new_h = max(1, int(ih * scale))

    return pygame.transform.smoothscale(img, (new_w, new_h))


def blit_centered_in_rect(screen, img, rect):
    img_rect = img.get_rect(center=rect.center)
    screen.blit(img, img_rect)


def draw_home_icon(screen, rect):
    draw_rounded_panel(screen, rect, BG_COLOR, radius=18)
    x, y, w, h = rect
    roof = [(x + w // 2, y + 8), (x + 10, y + 28), (x + w - 10, y + 28)]
    body = pygame.Rect(x + 16, y + 24, w - 32, h - 30)
    pygame.draw.polygon(screen, WHITE, roof)
    pygame.draw.rect(screen, WHITE, body, border_radius=6)


def draw_gear_icon(screen, rect):
    draw_rounded_panel(screen, rect, BG_COLOR, radius=18)
    cx, cy = rect.center
    for angle in range(0, 360, 45):
        vec = pygame.math.Vector2(18, 0).rotate(angle)
        tooth = pygame.Rect(0, 0, 8, 14)
        tooth.center = (cx + vec.x, cy + vec.y)
        pygame.draw.rect(screen, WHITE, tooth, border_radius=3)
    pygame.draw.circle(screen, WHITE, (cx, cy), 18)
    pygame.draw.circle(screen, BG_COLOR, (cx, cy), 8)


def draw_lock_icon(screen, center, scale=1.0):
    cx, cy = center

    shackle_rect = pygame.Rect(0, 0, int(34 * scale), int(28 * scale))
    shackle_rect.center = (cx, cy - int(12 * scale))
    pygame.draw.arc(screen, WHITE, shackle_rect, 3.14159, 0, max(3, int(5 * scale)))

    body_rect = pygame.Rect(0, 0, int(42 * scale), int(32 * scale))
    body_rect.center = (cx, cy + int(12 * scale))
    pygame.draw.rect(screen, WHITE, body_rect, border_radius=max(4, int(6 * scale)))

    hole_radius = max(3, int(4 * scale))
    pygame.draw.circle(screen, (70, 70, 70), (cx, cy + int(10 * scale)), hole_radius)
    pygame.draw.rect(screen, (70, 70, 70), (cx - 2, cy + int(10 * scale), 4, int(8 * scale)))


def draw_square_preview(screen, center, color, label_text, color_name, label_font, name_font):
    shadow = pygame.Rect(0, 0, 200, 200)
    shadow.center = (center[0] + 8, center[1] + 12)
    draw_rounded_panel(screen, shadow, SHADOW, radius=28)

    rect = pygame.Rect(0, 0, 200, 200)
    rect.center = center
    draw_rounded_panel(screen, rect, color, border_color=BLACK, border_width=7, radius=28)
    draw_text(screen, label_text, label_font, WHITE, center=rect.center)

    name_rect = pygame.Rect(rect.x + 24, rect.bottom + 20, 152, 44)
    draw_rounded_panel(screen, name_rect, NAVY, radius=16)
    draw_text(screen, color_name, name_font, WHITE, center=name_rect.center)


def draw_color_button(screen, rect, font):
    draw_rounded_panel(screen, rect, DARK_BLUE, radius=22)

    icon_center = (rect.x + 36, rect.centery)
    pygame.draw.circle(screen, (220, 230, 255), icon_center, 15)
    pygame.draw.circle(screen, (180, 190, 220), icon_center, 15, 2)
    pygame.draw.circle(screen, (255, 90, 90), (icon_center[0] + 10, icon_center[1] + 8), 6)

    draw_text(screen, "Color 1", font, WHITE, center=(rect.x + 118, rect.centery))


def draw_map_preview_image(screen, image_rect, image_path):
    img = load_image_keep_ratio(image_path, (image_rect.width, image_rect.height))
    if img:
        blit_centered_in_rect(screen, img, image_rect)
    else:
        draw_rounded_panel(screen, image_rect, (45, 45, 55), radius=12)


def draw_locked_overlay(screen, target_rect, font, lock_scale=1.0):
    overlay = pygame.Surface((target_rect.width, target_rect.height), pygame.SRCALPHA)
    overlay.fill(LOCK_OVERLAY)
    screen.blit(overlay, target_rect.topleft)

    draw_lock_icon(screen, (target_rect.centerx, target_rect.centery - 10), scale=lock_scale)
    draw_text(screen, "Locked", font, WHITE, center=(target_rect.centerx, target_rect.centery + 42))


def draw_main_map_card(screen, rect, map_data, title_font, small_font, is_locked):
    draw_rounded_panel(screen, rect, (230, 235, 240), border_color=(80, 100, 110), border_width=4, radius=18)

    inner = rect.inflate(-22, -22)
    image_rect = pygame.Rect(inner.x, inner.y, inner.width, inner.height - 52)

    draw_map_preview_image(screen, image_rect, map_data["image"])

    if is_locked:
        draw_locked_overlay(screen, image_rect, small_font, lock_scale=1.0)

    name_bar = pygame.Rect(inner.x + 10, inner.bottom - 45, inner.width - 20, 36)
    draw_rounded_panel(screen, name_bar, NAVY, radius=12)
    draw_text(screen, map_data["name"], title_font, WHITE, center=name_bar.center)


def draw_side_map_thumbnail(screen, rect, map_data, font, is_locked):
    draw_rounded_panel(screen, rect, (220, 225, 230), border_color=(80, 100, 110), border_width=3, radius=16)

    inner = rect.inflate(-10, -10)
    draw_rounded_panel(screen, inner, (30, 30, 40), radius=10)

    image_rect = inner.inflate(-6, -6)
    draw_map_preview_image(screen, image_rect, map_data["image"])

    if is_locked:
        draw_locked_overlay(screen, image_rect, font, lock_scale=0.78)


def draw_go_button(screen, rect, mouse_pos, font):
    go_fill = (250, 214, 76) if rect.collidepoint(mouse_pos) else YELLOW
    draw_rounded_panel(screen, rect, go_fill, border_color=(210, 170, 40), border_width=5, radius=20)
    go_inner = rect.inflate(-8, -10)
    pygame.draw.rect(screen, (240, 190, 70), go_inner, border_radius=16)
    draw_text(screen, "GO!", font, WHITE, center=(rect.centerx, rect.centery - 2))


def draw_popup_overlay(screen):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 110))
    screen.blit(overlay, (0, 0))


def get_color_popup_rects():
    popup_rect = pygame.Rect(0, 0, 420, 260)
    popup_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    swatches = []
    start_x = popup_rect.x + 42
    start_y = popup_rect.y + 85
    size = 58
    gap = 20

    for i in range(len(PLAYER_COLORS)):
        row = i // 4
        col = i % 4
        rect = pygame.Rect(
            start_x + col * (size + gap),
            start_y + row * (size + gap),
            size,
            size
        )
        swatches.append(rect)

    close_rect = pygame.Rect(popup_rect.right - 52, popup_rect.y + 16, 32, 32)
    return popup_rect, swatches, close_rect


def draw_color_popup(screen, popup_for_player, popup_rect, swatches, close_rect, title_font, small_font, current_index):
    draw_popup_overlay(screen)
    draw_rounded_panel(screen, popup_rect, (240, 244, 248), border_color=NAVY, border_width=4, radius=22)

    title = "Choose P1 Color" if popup_for_player == 1 else "Choose P2 Color"
    draw_text(screen, title, title_font, NAVY, center=(popup_rect.centerx, popup_rect.y + 35))

    draw_rounded_panel(screen, close_rect, (220, 80, 80), radius=10)
    draw_text(screen, "X", small_font, WHITE, center=close_rect.center)

    for i, rect in enumerate(swatches):
        color_name, color_value = PLAYER_COLORS[i]
        border_color = BLACK if i == current_index else (140, 150, 160)
        border_width = 5 if i == current_index else 2
        draw_rounded_panel(screen, rect, color_value, border_color=border_color, border_width=border_width, radius=12)
        draw_text(screen, color_name, small_font, NAVY, center=(rect.centerx, rect.bottom + 16))


#Main menu actual logic and function
def run_menu(screen):
    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("arialblack", 28)
    medium_font = pygame.font.SysFont("arialblack", 22)
    small_font = pygame.font.SysFont("arialblack", 18)
    go_font = pygame.font.SysFont("arialblack", 58)

    p1_color_index = 0
    p2_color_index = 1
    selected_map_index = 2  # start on The Underkeep

    popup_for_player = None
    popup_rect, swatches, close_rect = get_color_popup_rects()

    home_rect = pygame.Rect(40, 25, 58, 58)
    gear_rect = pygame.Rect(SCREEN_WIDTH - 98, 25, 58, 58)

    p1_preview_center = (360, 360)
    p2_preview_center = (1240, 360)

    p1_color_btn = pygame.Rect(140, 610, 170, 78)
    p2_color_btn = pygame.Rect(SCREEN_WIDTH - 310, 610, 170, 78)

    map_card_rect = pygame.Rect(SCREEN_WIDTH // 2 - 170, 28, 340, 270)
    left_arrow_rect = pygame.Rect(map_card_rect.x - 42, 118, 34, 78)
    right_arrow_rect = pygame.Rect(map_card_rect.right + 8, 118, 34, 78)

    locked_thumb_left = pygame.Rect(map_card_rect.x - 155, 76, 112, 152)
    locked_thumb_right = pygame.Rect(map_card_rect.right + 43, 76, 112, 152)

    go_rect = pygame.Rect(SCREEN_WIDTH // 2 - 130, 705, 260, 98)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if popup_for_player is not None:
                    if close_rect.collidepoint(mouse_pos):
                        popup_for_player = None
                    else:
                        for i, rect in enumerate(swatches):
                            if rect.collidepoint(mouse_pos):
                                if popup_for_player == 1:
                                    p1_color_index = i
                                else:
                                    p2_color_index = i
                                popup_for_player = None
                                break
                else:
                    if p1_color_btn.collidepoint(mouse_pos):
                        popup_for_player = 1

                    elif p2_color_btn.collidepoint(mouse_pos):
                        popup_for_player = 2

                    elif left_arrow_rect.collidepoint(mouse_pos):
                        selected_map_index = (selected_map_index - 1) % len(MAPS)

                    elif right_arrow_rect.collidepoint(mouse_pos):
                        selected_map_index = (selected_map_index + 1) % len(MAPS)

                    elif go_rect.collidepoint(mouse_pos):
                        if UNLOCKED_MAPS[selected_map_index]:
                            return {
                                "p1_color": PLAYER_COLORS[p1_color_index][1],
                                "p2_color": PLAYER_COLORS[p2_color_index][1],
                                "p1_color_name": PLAYER_COLORS[p1_color_index][0],
                                "p2_color_name": PLAYER_COLORS[p2_color_index][0],
                                "map_index": selected_map_index,
                                "map_name": MAPS[selected_map_index]["name"],
                            }

        screen.fill(BG_COLOR)

        draw_home_icon(screen, home_rect)
        draw_gear_icon(screen, gear_rect)

        p1_color_name, p1_color = PLAYER_COLORS[p1_color_index]
        p2_color_name, p2_color = PLAYER_COLORS[p2_color_index]

        draw_square_preview(screen, p1_preview_center, p1_color, "P1", p1_color_name, medium_font, small_font)
        draw_square_preview(screen, p2_preview_center, p2_color, "P2", p2_color_name, medium_font, small_font)

        draw_color_button(screen, p1_color_btn, small_font)
        draw_color_button(screen, p2_color_btn, small_font)

        current_locked = not UNLOCKED_MAPS[selected_map_index]
        draw_main_map_card(
            screen,
            map_card_rect,
            MAPS[selected_map_index],
            medium_font,
            small_font,
            current_locked
        )

        left_index = (selected_map_index - 1) % len(MAPS)
        right_index = (selected_map_index + 1) % len(MAPS)

        draw_side_map_thumbnail(
            screen,
            locked_thumb_left,
            MAPS[left_index],
            small_font,
            not UNLOCKED_MAPS[left_index]
        )

        draw_side_map_thumbnail(
            screen,
            locked_thumb_right,
            MAPS[right_index],
            small_font,
            not UNLOCKED_MAPS[right_index]
        )

        draw_arrow_button(screen, left_arrow_rect, "left")
        draw_arrow_button(screen, right_arrow_rect, "right")

        if UNLOCKED_MAPS[selected_map_index]:
            draw_go_button(screen, go_rect, mouse_pos, go_font)
        else:
            draw_rounded_panel(screen, go_rect, (150, 150, 150), border_color=(110, 110, 110), border_width=5, radius=20)
            draw_text(screen, "LOCKED", medium_font, WHITE, center=go_rect.center)

        if popup_for_player == 1:
            draw_color_popup(screen, 1, popup_rect, swatches, close_rect, medium_font, small_font, p1_color_index)
        elif popup_for_player == 2:
            draw_color_popup(screen, 2, popup_rect, swatches, close_rect, medium_font, small_font, p2_color_index)

        pygame.display.flip()
        clock.tick(60)


#show game
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Menu Test")

    selected_data = run_menu(screen)
    print(selected_data)

    pygame.quit()