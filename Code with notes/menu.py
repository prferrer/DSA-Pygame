"""
menu.py  –  PvP Shooter Game – Character & Map Selection Screen
================================================================
HOW TO CONNECT TO main.py
--------------------------
    from menu import run_menu

    result = run_menu()
    if result:
        p1_color, p1_hat, p2_color, p2_hat, chosen_map = result
        # pass these into your game initialisation
    else:
        pygame.quit()
        sys.exit()
"""

import os
import math
import sys
import pygame

HATS = ["None", "Crown", "Top", "Cowboy", "Duck", "Party", "Pirate"]

MAPS = ["Greenwood Village", "Meadow Crossing", "The Underkeep",]

_HERE   = os.path.dirname(os.path.abspath(__file__))
HAT_DIR = os.path.join(_HERE, "assets", "hats")
MAP_DIR = os.path.join(_HERE, "assets", "maps")

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

TARGET_W, TARGET_H = 1536, 864   # logical canvas (fits 1920x1080 @ 125% scale)
FPS = 60

BG_TOP   = ( 18,  32,  70)
BG_BOT   = ( 30,  55, 105)
PANEL_BG = ( 16,  30,  65)
PANEL_RIM= ( 55,  88, 160)
GOLD     = (255, 200,  40)
GOLD_D   = (190, 130,   5)
CYAN     = ( 70, 210, 255)
WHITE    = (255, 255, 255)
BLACK    = (  0,   0,   0)

PLAYER_COLORS = [
    ("Blue",   ( 50, 110, 255)),
    ("Red",    (220,  35,  35)),
    ("Green",  ( 35, 200,  75)),
    ("Yellow", (245, 215,  25)),
    ("Purple", (160,  50, 225)),
    ("Orange", (245, 130,  18)),
    ("Cyan",   ( 18, 215, 215)),
    ("Pink",   (255,  75, 165)),
]

# ──────────────────────────────────────────────────────────────────────────────
# ASSET LOADER
# ──────────────────────────────────────────────────────────────────────────────

_hat_images = {}
_map_images = {}


def _load_assets():
    for name in HATS:
        path = os.path.join(HAT_DIR, f"{name}.png")
        if os.path.isfile(path):
            try:
                _hat_images[name] = pygame.image.load(path).convert_alpha()
            except Exception:
                try:
                    _hat_images[name] = pygame.image.load(path)
                except Exception:
                    _hat_images[name] = None
        else:
            _hat_images[name] = None

    for name in MAPS:
        path = os.path.join(MAP_DIR, f"{name}.png")
        if os.path.isfile(path):
            try:
                _map_images[name] = pygame.image.load(path).convert()
            except Exception:
                try:
                    _map_images[name] = pygame.image.load(path)
                except Exception:
                    _map_images[name] = None
        else:
            _map_images[name] = None


# ──────────────────────────────────────────────────────────────────────────────
# DRAWING HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def draw_rounded_rect(surf, color, rect, radius=16, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_gradient_rect(surf, rect, top_color, bot_color):
    x, y, w, h = rect
    for i in range(h):
        t  = i / max(h - 1, 1)
        rc = int(top_color[0] + (bot_color[0] - top_color[0]) * t)
        gc = int(top_color[1] + (bot_color[1] - top_color[1]) * t)
        bc = int(top_color[2] + (bot_color[2] - top_color[2]) * t)
        pygame.draw.line(surf, (rc, gc, bc), (x, y + i), (x + w - 1, y + i))


# ──────────────────────────────────────────────────────────────────────────────
# CHARACTER PREVIEW  (square only – no body)
# ──────────────────────────────────────────────────────────────────────────────

def draw_character(surf, cx, cy, size, body_color, hat_name):
    """
    Draw a plain coloured square with two eyes and a hat on top.
    cx, cy = centre of the square.
    size   = side length of the square.
    Hat is drawn above the square, clipped to its width.
    """
    half = size // 2
    sq   = pygame.Rect(cx - half, cy - half, size, size)

    # drop shadow
    shadow = pygame.Surface((size + 8, 10), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow, (0, 0, 0, 70), shadow.get_rect())
    surf.blit(shadow, (cx - half - 4, cy + half - 2))

    # body square
    pygame.draw.rect(surf, BLACK,      sq.inflate(4, 4), border_radius=6)
    pygame.draw.rect(surf, body_color, sq,               border_radius=5)

    # eyes
    ey      = cy - half // 4
    eye_r   = max(4, size // 9)
    pupil_r = max(2, eye_r // 2)
    for ex in (cx - half // 3, cx + half // 3):
        pygame.draw.circle(surf, (30, 30, 50), (ex, ey), eye_r + 1)
        pygame.draw.circle(surf, WHITE,        (ex, ey), eye_r)
        pygame.draw.circle(surf, (20, 20, 30), (ex, ey), pupil_r)

    # ── hat ───────────────────────────────────────────────────────────────────
    hat_img = _hat_images.get(hat_name)

    if hat_img is not None:
        hw    = size
        ratio = hw / hat_img.get_width()
        hh    = int(hat_img.get_height() * ratio)
        scaled_hat = pygame.transform.smoothscale(hat_img, (hw, hh))
        hat_y = cy - half - int(hh * 0.72)

        surf.blit(scaled_hat, (cx - hw // 2, hat_y))
    else:
        # procedural fallback – draws hat above square top edge
        hat_top = cy - half    # y of the square's top edge
        hh      = half // 2    # generic hat height

        if hat_name == "Crown":
            base_y = hat_top
            pts = [
                (cx - half,      base_y),
                (cx - half + 6,  base_y - hh),
                (cx - 5,         base_y - hh // 2),
                (cx,             base_y - hh - 4),
                (cx + 5,         base_y - hh // 2),
                (cx + half - 6,  base_y - hh),
                (cx + half,      base_y),
            ]
            pygame.draw.polygon(surf, GOLD_D, pts)
            pygame.draw.polygon(surf, GOLD,   pts, 2)
            for gx in (cx - half // 2, cx, cx + half // 2):
                pygame.draw.circle(surf, (220, 40, 40),
                                   (gx, base_y - 6), max(2, half // 8))

        elif hat_name == "Top Hat":
            brim = pygame.Rect(cx - half - 4, hat_top - 6,  size + 8, 8)
            body = pygame.Rect(cx - half + 6, hat_top - hh - 4, size - 12, hh)
            pygame.draw.rect(surf, (25, 15,  8), body, border_radius=3)
            pygame.draw.rect(surf, (25, 15,  8), brim, border_radius=3)
            pygame.draw.rect(surf, (70, 45, 15), body, 2, border_radius=3)

        elif hat_name == "Cowboy":
            brim = pygame.Rect(cx - half - 10, hat_top - 8, size + 20, 10)
            dome = pygame.Rect(cx - half + 4,  hat_top - hh - 2, size - 8, hh)
            pygame.draw.ellipse(surf, (110, 65, 18), brim)
            pygame.draw.rect  (surf, (130, 75, 22), dome, border_radius=6)
            pygame.draw.ellipse(surf, ( 80, 45, 10), brim, 2)
            pygame.draw.line  (surf, (55, 25, 5),
                               (cx - half + 4, hat_top - 4),
                               (cx + half - 4, hat_top - 4), 3)

        elif hat_name == "Helmet":
            helm = pygame.Rect(cx - half - 2, hat_top - hh - 4, size + 4, hh + 8)
            pygame.draw.rect(surf, ( 70,  85, 100), helm, border_radius=10)
            pygame.draw.rect(surf, (115, 130, 145), helm, 2, border_radius=10)
            visor = pygame.Rect(cx - half + 6, hat_top - 8, size - 12, 10)
            pygame.draw.rect(surf, (40, 55, 70), visor, border_radius=3)

        elif hat_name == "Cap":
            dome = pygame.Rect(cx - half + 4, hat_top - hh, size - 8, hh + 4)
            brim = pygame.Rect(cx,            hat_top - 4,  half + 6,  7)
            pygame.draw.rect(surf, (190, 25, 25), dome, border_radius=10)
            pygame.draw.rect(surf, (155, 15, 15), brim, border_radius=4)
            pygame.draw.rect(surf, (230, 60, 60), dome, 2, border_radius=10)

        elif hat_name == "Wizard":
            tip    = (cx,        hat_top - hh * 2 - 4)
            base_l = (cx - half, hat_top)
            base_r = (cx + half, hat_top)
            pygame.draw.polygon(surf, ( 75, 18, 135), [tip, base_l, base_r])
            pygame.draw.polygon(surf, (125, 55, 195), [tip, base_l, base_r], 2)
            for sx, sy in ((cx - 7, hat_top - hh), (cx + 5, hat_top - hh // 2)):
                pygame.draw.circle(surf, GOLD, (sx, sy), 3)
        # "None" -> draw nothing
        
def draw_hat_only(surf, cx, cy, size, hat_name):
    """
    Draws only the selected hat, without showing the character body.
    Used for the hat selection grid.
    """
    hat_img = _hat_images.get(hat_name)

    if hat_name == "None":
        font = pygame.font.SysFont("Arial", 18)
        lbl = font.render("None", True, (160, 185, 230))
        surf.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))
        return

    if hat_img is not None:
        hw = size
        ratio = hw / hat_img.get_width()
        hh = int(hat_img.get_height() * ratio)

        if hh > size:
            hh = size
            ratio = hh / hat_img.get_height()
            hw = int(hat_img.get_width() * ratio)

        scaled_hat = pygame.transform.smoothscale(hat_img, (hw, hh))
        surf.blit(scaled_hat, (cx - hw // 2, cy - hh // 2))
    else:
        # fallback if PNG is missing
        preview_size = size // 2
        draw_character(surf, cx, cy + 25, preview_size, (80, 120, 220), hat_name)


# ──────────────────────────────────────────────────────────────────────────────
# MAP THUMBNAIL
# ──────────────────────────────────────────────────────────────────────────────

_MAP_GRAD = {
    "Greenwood Village":  [(35, 22, 55), (75, 48, 28)],
    "Meadow Crossing":  [(190, 135, 38), (115, 75, 18)],
    "The Underkeep": [(75, 155, 215), (145, 198, 255)],
}


def draw_map_thumbnail(surf, rect, map_name):
    img = _map_images.get(map_name)
    if img is not None:
        scaled = pygame.transform.smoothscale(img, (rect[2], rect[3]))
        surf.blit(scaled, (rect[0], rect[1]))
    else:
        x, y, w, h = rect
        cols = _MAP_GRAD.get(map_name, [(50, 50, 80), (80, 80, 120)])
        draw_gradient_rect(surf, rect, cols[0], cols[1])

        if map_name == "Castle Rock":
            for tx in (x + 10, x + w - 30):
                pygame.draw.rect(surf, (20, 12, 32), (tx, y + h // 3, 20, h))
                pygame.draw.rect(surf, (20, 12, 32), (tx - 5, y + h // 3, 30, 10))
            pygame.draw.rect(surf, (12, 8, 22),
                             (x + w // 2 - 14, y + h // 2, 28, h))
        elif map_name == "Desert Duel":
            pygame.draw.ellipse(surf, (170, 115, 28),
                                (x - 12, y + h * 2 // 3, w // 2 + 12, h // 2))
            pygame.draw.ellipse(surf, (150, 95, 18),
                                (x + w // 3, y + h * 2 // 3, w // 2 + 12, h // 2))
        elif map_name == "Ice Fortress":
            for ix in range(x + 8, x + w, 16):
                pts = [(ix, y + h // 2), (ix + 7, y + h // 2 - 22),
                       (ix + 14, y + h // 2)]
                pygame.draw.polygon(surf, (195, 228, 255), pts)
        elif map_name == "Rooftop Rush":
            for bx, bh in ((x + 5, h // 2), (x + w // 3, h * 2 // 5),
                           (x + w * 2 // 3 - 5, h // 3)):
                pygame.draw.rect(surf, (28, 28, 48), (bx, y + h - bh, 30, bh))
        elif map_name == "Jungle Ruins":
            for px in (x + 14, x + w - 34):
                pygame.draw.rect(surf, (45, 75, 28), (px, y + h // 4, 20, h))
            for vx in range(x + 6, x + w, 22):
                pygame.draw.line(surf, (18, 75, 28),
                                 (vx, y), (vx + 6, y + h // 2), 2)

    pygame.draw.rect(surf, (180, 200, 230), rect, 2)


# ──────────────────────────────────────────────────────────────────────────────
# UI WIDGETS
# ──────────────────────────────────────────────────────────────────────────────

class ColorSwatch:
    def __init__(self, rect, color_rgb, label):
        self.rect     = pygame.Rect(rect)
        self.color    = color_rgb
        self.label    = label
        self.selected = False
        self.hovered  = False

    def draw(self, surf):
        r = self.rect
        if self.selected:
            pygame.draw.rect(surf, GOLD, r.inflate(8, 8), border_radius=10)
        elif self.hovered:
            pygame.draw.rect(surf, CYAN, r.inflate(4, 4), border_radius=9)
        pygame.draw.rect(surf, self.color, r, border_radius=8)
        pygame.draw.rect(surf, WHITE,      r, 2, border_radius=8)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class HatButton:
    """2-column scrollable hat picker cell."""
    BTN_W = 110
    BTN_H = 110

    def __init__(self, rect, hat_name, body_color):
        self.rect       = pygame.Rect(rect)
        self.hat_name   = hat_name
        self.body_color = body_color
        self.selected   = False
        self.hovered    = False

    def draw(self, surf, font_small):
        r = self.rect
        bg = (50, 72, 125) if self.hovered else (35, 52, 98)
        bc = GOLD if self.selected else (70, 100, 175)

        draw_rounded_rect(surf, bg, r, radius=10, border=3, border_color=bc)

        # Draw only the hat, not the whole character
        hat_size = min(r.width - 22, r.height - 38)
        draw_hat_only(surf, r.centerx, r.centery - 10, hat_size, self.hat_name)

        color = WHITE if self.selected else (160, 185, 230)
        lbl = font_small.render(self.hat_name, True, color)
        surf.blit(lbl, (r.centerx - lbl.get_width() // 2, r.bottom - 18))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class ScrollArrow:
    def __init__(self, rect, direction):
        self.rect      = pygame.Rect(rect)
        self.direction = direction
        self.hovered   = False

    def draw(self, surf):
        r  = self.rect
        cx, cy = r.centerx, r.centery
        hw = r.width // 3
        color = GOLD if self.hovered else (160, 185, 230)
        if self.direction == 'up':
            pts = [(cx, cy - hw), (cx - hw, cy + hw), (cx + hw, cy + hw)]
        else:
            pts = [(cx, cy + hw), (cx - hw, cy - hw), (cx + hw, cy - hw)]
        pygame.draw.polygon(surf, color, pts)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class MapArrow:
    def __init__(self, rect, direction):
        self.rect      = pygame.Rect(rect)
        self.direction = direction
        self.hovered   = False

    def draw(self, surf):
        r  = self.rect
        cx, cy = r.centerx, r.centery
        hw = r.width // 3
        color = GOLD if self.hovered else (180, 200, 230)
        if self.direction == 'left':
            pts = [(cx + hw, cy - hw), (cx - hw, cy), (cx + hw, cy + hw)]
        else:
            pts = [(cx - hw, cy - hw), (cx + hw, cy), (cx - hw, cy + hw)]
        pygame.draw.polygon(surf, color, pts)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class GoButton:
    def __init__(self, rect):
        self.rect    = pygame.Rect(rect)
        self.hovered = False
        self._t      = 0.0

    def update(self, dt):
        self._t += dt

    def draw(self, surf, font):
        sc = 1.0 + 0.025 * math.sin(self._t * 3.8)
        r  = self.rect
        w2 = int(r.width * sc);  h2 = int(r.height * sc)
        r2 = pygame.Rect(r.centerx - w2 // 2, r.centery - h2 // 2, w2, h2)
        top = (255, 225, 55) if self.hovered else (245, 195, 20)
        bot = (195, 140,  8) if self.hovered else (175, 108,  4)
        draw_gradient_rect(surf, r2, top, bot)
        pygame.draw.rect(surf, (255, 255, 185), r2, 3, border_radius=14)
        lbl = font.render("GO!", True, (55, 28, 0))
        surf.blit(lbl, (r2.centerx - lbl.get_width()  // 2,
                        r2.centery - lbl.get_height() // 2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


# ──────────────────────────────────────────────────────────────────────────────
# BACKGROUND PARTICLES
# ──────────────────────────────────────────────────────────────────────────────

class Particle:
    def __init__(self, W, H):
        import random
        self.W, self.H = W, H
        self.x     = random.uniform(0, W)
        self.y     = random.uniform(0, H)
        self.r     = random.uniform(1, 2.5)
        self.speed = random.uniform(12, 35)
        self.alpha = random.randint(25, 90)

    def update(self, dt):
        self.y -= self.speed * dt
        if self.y < -8:
            import random
            self.y = self.H + 8
            self.x = random.uniform(0, self.W)

    def draw(self, surf):
        s = pygame.Surface((int(self.r * 2) + 1, int(self.r * 2) + 1),
                           pygame.SRCALPHA)
        pygame.draw.circle(s, (*CYAN, self.alpha),
                           (int(self.r), int(self.r)), int(self.r))
        surf.blit(s, (int(self.x - self.r), int(self.y - self.r)))


# ──────────────────────────────────────────────────────────────────────────────
# MAIN MENU FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

def run_menu(screen=None):
    pygame.init()
    _load_assets()

    # ── window ────────────────────────────────────────────────────────────────
    if screen is None:
        info = pygame.display.Info()
        W = info.current_w if info.current_w > 0 else TARGET_W
        H = info.current_h if info.current_h > 0 else TARGET_H
        if W <= 0 or H <= 0:
            W, H = TARGET_W, TARGET_H
        screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        pygame.display.set_caption("PvP Shooter – Select Characters & Map")
    else:
        W, H = screen.get_size()

    canvas = pygame.Surface((TARGET_W, TARGET_H))
    CW, CH = TARGET_W, TARGET_H
    clock  = pygame.time.Clock()

    # ── fonts ─────────────────────────────────────────────────────────────────
    def F(size, bold=False):
        try:
            return pygame.font.SysFont(
                "Arial Rounded MT Bold" if bold else "Arial", size, bold=bold)
        except Exception:
            return pygame.font.Font(None, size)

    font_hdr   = F(34, bold=True)
    font_label = F(22)
    font_small = F(17)
    font_go    = F(58, bold=True)

    # ── layout constants ──────────────────────────────────────────────────────
    # ── layout constants ──────────────────────────────────────────────────────
    PAD  = 28
    MID_X = CW // 2
    P_W  = 340
    P_Y  = 45
    P_H  = CH - 60

    # Player panels must be created first
    p1_panel = pygame.Rect(PAD, P_Y, P_W, P_H)
    p2_panel = pygame.Rect(CW - PAD - P_W, P_Y, P_W, P_H)

    # Name box positions
    NAME_BOX_Y = P_Y + 38
    NAME_BOX_H = 34

    p1_name_box = pygame.Rect(
        p1_panel.x + 55,
        NAME_BOX_Y,
        p1_panel.width - 110,
        NAME_BOX_H
    )

    p2_name_box = pygame.Rect(
        p2_panel.x + 55,
        NAME_BOX_Y,
        p2_panel.width - 110,
        NAME_BOX_H
    )

    map_panel = pygame.Rect(MID_X - 185, P_Y, 370, 300)

    thumb_rect = pygame.Rect(
        map_panel.x + 28,
        map_panel.y + 50,
        map_panel.width - 56,
        170
    )

    arrow_l = MapArrow((map_panel.x + 2, thumb_rect.centery - 18, 26, 36), 'left')
    arrow_r = MapArrow((map_panel.right - 28, thumb_rect.centery - 18, 26, 36), 'right')

    go_btn = GoButton((MID_X - 105, map_panel.bottom + 36, 210, 66))

    # ── colour swatches ───────────────────────────────────────────────────────
    SW    = 48
    S_GAP = 9
    COLS  = 4

    PREVIEW_CY    = P_Y + 165    # centre-y of the big character preview
    COLOR_LABEL_Y = P_Y + 265
    SW_Y          = COLOR_LABEL_Y + 28

    def swatch_origin(panel):
        total_w = COLS * SW + (COLS - 1) * S_GAP
        return panel.x + (panel.width - total_w) // 2

    def make_swatches(panel):
        ox = swatch_origin(panel)
        out = []
        for i, (name, rgb) in enumerate(PLAYER_COLORS):
            col = i % COLS
            row = i // COLS
            rx  = ox + col * (SW + S_GAP)
            ry  = SW_Y + row * (SW + S_GAP)
            out.append(ColorSwatch((rx, ry, SW, SW), rgb, name))
        return out

    p1_swatches = make_swatches(p1_panel)
    p2_swatches = make_swatches(p2_panel)

    # ── hat buttons – 2-column scrollable grid ────────────────────────────────
    HB_W   = HatButton.BTN_W   # 110
    HB_H   = HatButton.BTN_H   # 110
    HB_GAP = 8
    HB_COLS = 2

    HAT_LABEL_Y = SW_Y + SW * 2 + S_GAP + 18
    HAT_GRID_Y  = HAT_LABEL_Y + 26

    _remaining   = (P_Y + P_H) - HAT_GRID_Y - 34
    VISIBLE_ROWS = max(1, _remaining // (HB_H + HB_GAP))
    total_hat_rows = math.ceil(len(HATS) / HB_COLS)

    def hat_grid_origin(panel):
        total_w = HB_COLS * HB_W + (HB_COLS - 1) * HB_GAP
        ox = panel.x + (panel.width - total_w) // 2
        return ox, HAT_GRID_Y

    def make_hat_buttons(panel, body_color):
        ox, oy = hat_grid_origin(panel)
        out = []
        for i, name in enumerate(HATS):
            col = i % HB_COLS
            row = i // HB_COLS
            rx  = ox + col * (HB_W + HB_GAP)
            ry  = oy + row * (HB_H + HB_GAP)
            out.append(HatButton((rx, ry, HB_W, HB_H), name, body_color))
        return out

    p1_hat_buttons = make_hat_buttons(p1_panel, PLAYER_COLORS[0][1])
    p2_hat_buttons = make_hat_buttons(p2_panel, PLAYER_COLORS[1][1])

    # scroll arrows – placed just below the visible grid area
    def scroll_arrow_rects(panel):
        _, oy = hat_grid_origin(panel)
        grid_h = VISIBLE_ROWS * (HB_H + HB_GAP) - HB_GAP
        ay = oy + grid_h + 6
        cx = panel.centerx
        return (pygame.Rect(cx - 30, ay, 26, 22),
                pygame.Rect(cx + 4,  ay, 26, 22))

    p1_up_r, p1_dn_r = scroll_arrow_rects(p1_panel)
    p2_up_r, p2_dn_r = scroll_arrow_rects(p2_panel)
    p1_up_arr = ScrollArrow(p1_up_r, 'up')
    p1_dn_arr = ScrollArrow(p1_dn_r, 'down')
    p2_up_arr = ScrollArrow(p2_up_r, 'up')
    p2_dn_arr = ScrollArrow(p2_dn_r, 'down')

    # ── state ─────────────────────────────────────────────────────────────────
    p1_color_idx  = 0
    p2_color_idx  = 1
    p1_hat_idx    = 0
    p2_hat_idx    = 0
    map_idx       = 0
    p1_hat_scroll = 0
    p2_hat_scroll = 0
    p1_name = "Player 1"
    p2_name = "Player 2"
    active_name_box = None

    p1_swatches[p1_color_idx].selected   = True
    p2_swatches[p2_color_idx].selected   = True
    p1_hat_buttons[p1_hat_idx].selected  = True
    p2_hat_buttons[p2_hat_idx].selected  = True

    # ── particles ─────────────────────────────────────────────────────────────
    particles = [Particle(CW, CH) for _ in range(55)]

    # ──────────────────────────────────────────────────────────────────────────
    # STATE HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def refresh_hat_preview_colors():
        for b in p1_hat_buttons:
            b.body_color = PLAYER_COLORS[p1_color_idx][1]
        for b in p2_hat_buttons:
            b.body_color = PLAYER_COLORS[p2_color_idx][1]

    def select_p1_color(idx):
        nonlocal p1_color_idx
        for s in p1_swatches: s.selected = False
        p1_color_idx = idx
        p1_swatches[idx].selected = True
        refresh_hat_preview_colors()

    def select_p2_color(idx):
        nonlocal p2_color_idx
        for s in p2_swatches: s.selected = False
        p2_color_idx = idx
        p2_swatches[idx].selected = True
        refresh_hat_preview_colors()

    def select_p1_hat(idx):
        nonlocal p1_hat_idx
        for b in p1_hat_buttons: b.selected = False
        p1_hat_idx = idx
        p1_hat_buttons[idx].selected = True

    def select_p2_hat(idx):
        nonlocal p2_hat_idx
        for b in p2_hat_buttons: b.selected = False
        p2_hat_idx = idx
        p2_hat_buttons[idx].selected = True

    # ──────────────────────────────────────────────────────────────────────────
    # SCROLLABLE HAT GRID DRAW  (only draws rows currently in view)
    # ──────────────────────────────────────────────────────────────────────────

    def draw_hat_grid(surf, buttons, scroll, panel, font_s):
        ox, oy      = hat_grid_origin(panel)
        clip_top    = HAT_GRID_Y - 2
        clip_bottom = HAT_GRID_Y + VISIBLE_ROWS * (HB_H + HB_GAP) - HB_GAP + 2

        for i, btn in enumerate(buttons):
            row    = i // HB_COLS
            draw_y = oy + row * (HB_H + HB_GAP) - scroll * (HB_H + HB_GAP)

            if draw_y + HB_H < clip_top or draw_y > clip_bottom:
                continue

            btn.rect.y = draw_y
            btn.draw(surf, font_s)

    # ──────────────────────────────────────────────────────────────────────────
    # DRAW FRAME
    # ──────────────────────────────────────────────────────────────────────────

    def draw_frame(dt):
        # background
        draw_gradient_rect(canvas, (0, 0, CW, CH), BG_TOP, BG_BOT)
        for gx in range(0, CW, 80):
            pygame.draw.line(canvas, (48, 68, 110), (gx, 0), (gx, CH), 1)
        for gy in range(0, CH, 80):
            pygame.draw.line(canvas, (48, 68, 110), (0, gy), (CW, gy), 1)
        for p in particles:
            p.update(dt)
            p.draw(canvas)

        # ── player panels ─────────────────────────────────────────────────────
        for (panel, label_txt, color_idx, hat_idx,
             swatches, hat_btns, scroll, is_p1,
             up_arr, dn_arr) in [
            (p1_panel, "Player 1", p1_color_idx, p1_hat_idx,
             p1_swatches, p1_hat_buttons, p1_hat_scroll, True,
             p1_up_arr, p1_dn_arr),
            (p2_panel, "Player 2", p2_color_idx, p2_hat_idx,
             p2_swatches, p2_hat_buttons, p2_hat_scroll, False,
             p2_up_arr, p2_dn_arr),
        ]:
            draw_rounded_rect(canvas, PANEL_BG, panel, radius=20,
                              border=3, border_color=PANEL_RIM)

            badge_color = CYAN if is_p1 else GOLD
            badge_r = pygame.Rect(panel.x + 30, panel.y - 16,
                                  panel.width - 60, 34)
            draw_rounded_rect(canvas, (16, 30, 65), badge_r, radius=12,
                              border=2, border_color=badge_color)
            lbl = font_hdr.render(label_txt, True, badge_color)
            canvas.blit(lbl, (badge_r.centerx - lbl.get_width() // 2,
                            badge_r.centery - lbl.get_height() // 2))

            # name input box
            name_box = p1_name_box if is_p1 else p2_name_box
            current_name = p1_name if is_p1 else p2_name

            box_border = GOLD if active_name_box == ("p1" if is_p1 else "p2") else PANEL_RIM
            draw_rounded_rect(canvas, (22, 40, 82), name_box, radius=8, border=2, border_color=box_border)

            name_surface = font_small.render(current_name, True, WHITE)
            canvas.blit(name_surface, (
                name_box.x + 10,
                name_box.centery - name_surface.get_height() // 2
            ))

            # big character preview
            body_rgb = PLAYER_COLORS[color_idx][1]
            hat_name  = HATS[hat_idx]
            draw_character(canvas, panel.centerx, PREVIEW_CY, 115,
                           body_rgb, hat_name)

            # COLOR label + swatches
            c_lbl = font_label.render("COLOR", True, (155, 185, 230))
            canvas.blit(c_lbl, (panel.centerx - c_lbl.get_width() // 2,
                                COLOR_LABEL_Y))
            for sw in swatches:
                sw.draw(canvas)

            # HAT label + scrollable grid
            h_lbl = font_label.render("HAT", True, (155, 185, 230))
            canvas.blit(h_lbl, (panel.centerx - h_lbl.get_width() // 2,
                                HAT_LABEL_Y))
            draw_hat_grid(canvas, hat_btns, scroll, panel, font_small)

            if total_hat_rows > VISIBLE_ROWS:
                up_arr.draw(canvas)
                dn_arr.draw(canvas)

        # ── map panel ─────────────────────────────────────────────────────────
        draw_rounded_rect(canvas, PANEL_BG, map_panel, radius=20,
                          border=3, border_color=PANEL_RIM)
        map_lbl = font_hdr.render("MAP", True, WHITE)
        canvas.blit(map_lbl, (MID_X - map_lbl.get_width() // 2,
                              map_panel.y + 10))

        draw_map_thumbnail(canvas, thumb_rect, MAPS[map_idx])

        nb = pygame.Rect(thumb_rect.x + 10, thumb_rect.bottom - 32,
                         thumb_rect.width - 20, 26)
        s2 = pygame.Surface((nb.width, nb.height), pygame.SRCALPHA)
        s2.fill((0, 0, 0, 155))
        canvas.blit(s2, nb.topleft)
        n_lbl = font_label.render(MAPS[map_idx], True, WHITE)
        canvas.blit(n_lbl, (nb.centerx - n_lbl.get_width() // 2,
                            nb.centery - n_lbl.get_height() // 2))

        arrow_l.draw(canvas)
        arrow_r.draw(canvas)
        tip = font_small.render("◄  ►  to browse maps", True, (145, 168, 210))
        canvas.blit(tip, (MID_X - tip.get_width() // 2,
                          thumb_rect.bottom + 12))

        # ── GO button ─────────────────────────────────────────────────────────
        go_btn.update(dt)
        go_btn.draw(canvas, font_go)

        # ── scale to screen ───────────────────────────────────────────────────
        sw, sh = screen.get_size()
        sc = min(sw / CW, sh / CH)
        bw = int(CW * sc);  bh = int(CH * sc)
        bx = (sw - bw) // 2;  by = (sh - bh) // 2
        scaled = pygame.transform.smoothscale(canvas, (bw, bh))
        screen.fill(BLACK)
        screen.blit(scaled, (bx, by))
        pygame.display.flip()
        return bx, by, sc

    # ──────────────────────────────────────────────────────────────────────────
    # EVENT LOOP
    # ──────────────────────────────────────────────────────────────────────────

    offset_x = offset_y = 0
    scale = 1.0

    def map_mouse(event):
        if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                              pygame.MOUSEMOTION):
            return event
        if scale == 0:
            return event
        mx = int((event.pos[0] - offset_x) / scale)
        my = int((event.pos[1] - offset_y) / scale)
        d  = {'pos': (mx, my)}
        if event.type == pygame.MOUSEMOTION:
            d['rel']     = event.rel
            d['buttons'] = event.buttons
        else:
            d['button'] = event.button
        return pygame.event.Event(event.type, d)

    running = True
    while running:
        dt     = clock.tick(FPS) / 1000.0
        events = [map_mouse(e) for e in pygame.event.get()]

        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit();  return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit();  return None

            # name box typing
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if p1_name_box.collidepoint(event.pos):
                    active_name_box = "p1"
                elif p2_name_box.collidepoint(event.pos):
                    active_name_box = "p2"
                else:
                    active_name_box = None

            if event.type == pygame.KEYDOWN and active_name_box is not None:
                if event.key == pygame.K_BACKSPACE:
                    if active_name_box == "p1":
                        p1_name = p1_name[:-1]
                    elif active_name_box == "p2":
                        p2_name = p2_name[:-1]

                elif event.key == pygame.K_RETURN:
                    active_name_box = None

                else:
                    if event.unicode.isprintable():
                        if active_name_box == "p1" and len(p1_name) < 12:
                            if p1_name == "Player 1":
                                p1_name = ""
                            p1_name += event.unicode

                        elif active_name_box == "p2" and len(p2_name) < 12:
                            if p2_name == "Player 2":
                                p2_name = ""
                            p2_name += event.unicode

            # map navigation
            if arrow_l.handle_event(event):
                map_idx = (map_idx - 1) % len(MAPS)
            if arrow_r.handle_event(event):
                map_idx = (map_idx + 1) % len(MAPS)

            # P1 colour
            for i, sw in enumerate(p1_swatches):
                if sw.handle_event(event): select_p1_color(i)

            # P2 colour
            for i, sw in enumerate(p2_swatches):
                if sw.handle_event(event): select_p2_color(i)

            # P1 hat buttons
            for i, btn in enumerate(p1_hat_buttons):
                if btn.handle_event(event): select_p1_hat(i)

            # P2 hat buttons
            for i, btn in enumerate(p2_hat_buttons):
                if btn.handle_event(event): select_p2_hat(i)

            # P1 hat scroll
            if total_hat_rows > VISIBLE_ROWS:
                if p1_up_arr.handle_event(event):
                    p1_hat_scroll = max(0, p1_hat_scroll - 1)
                if p1_dn_arr.handle_event(event):
                    p1_hat_scroll = min(total_hat_rows - VISIBLE_ROWS,
                                        p1_hat_scroll + 1)
                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    cmx = int((mx - offset_x) / scale)
                    cmy = int((my - offset_y) / scale)
                    if p1_panel.collidepoint(cmx, cmy):
                        p1_hat_scroll = max(0, min(
                            total_hat_rows - VISIBLE_ROWS,
                            p1_hat_scroll - event.y))

            # P2 hat scroll
            if total_hat_rows > VISIBLE_ROWS:
                if p2_up_arr.handle_event(event):
                    p2_hat_scroll = max(0, p2_hat_scroll - 1)
                if p2_dn_arr.handle_event(event):
                    p2_hat_scroll = min(total_hat_rows - VISIBLE_ROWS,
                                        p2_hat_scroll + 1)
                if event.type == pygame.MOUSEWHEEL:
                    mx, my = pygame.mouse.get_pos()
                    cmx = int((mx - offset_x) / scale)
                    cmy = int((my - offset_y) / scale)
                    if p2_panel.collidepoint(cmx, cmy):
                        p2_hat_scroll = max(0, min(
                            total_hat_rows - VISIBLE_ROWS,
                            p2_hat_scroll - event.y))

            # GO!
            if go_btn.handle_event(event):
                final_p1_name = p1_name.strip() if p1_name.strip() else "Player 1"
                final_p2_name = p2_name.strip() if p2_name.strip() else "Player 2"

                return (
                    final_p1_name,
                    PLAYER_COLORS[p1_color_idx][1],
                    HATS[p1_hat_idx],

                    final_p2_name,
                    PLAYER_COLORS[p2_color_idx][1],
                    HATS[p2_hat_idx],

                    MAPS[map_idx],
                )

        offset_x, offset_y, scale = draw_frame(dt)

    return None


# ──────────────────────────────────────────────────────────────────────────────
# STANDALONE TEST  (python menu.py)
# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    result = run_menu()
    if result:
        p1_name, p1c, p1h, p2_name, p2c, p2h, m = result
        print(f"{p1_name} → color={p1c}  hat={p1h}")
        print(f"{p2_name} → color={p2c}  hat={p2h}")
        print(f"Map → {m}")
    pygame.quit()
    sys.exit()
