import pygame
import random
import sys
import math
from abc import ABC, abstractmethod

pygame.init()

# ── Konstanta global ────────────────────────────────────────────
SCREEN_W, SCREEN_H = 620, 720
FPS          = 60
ROAD_LEFT    = 90
ROAD_RIGHT   = 530
LANE_COUNT   = 5
LANE_W       = (ROAD_RIGHT - ROAD_LEFT) // LANE_COUNT
LANES        = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(LANE_COUNT)]

# Palet warna
BLACK      = (20,  20,  20)
WHITE      = (245, 245, 245)
GRAY       = (90,  90,  90)
ROAD_COL   = (55,  55,  55)
GRASS_COL  = (40, 110,  40)
DASH_COL   = (210, 210, 210)
YELLOW     = (255, 215,  40)
RED        = (210,  45,  45)
BLUE       = (40,  110, 220)
GREEN      = (40,  180,  90)
ORANGE     = (240, 130,  20)
PURPLE     = (140,  60, 200)
CYAN       = (0,   200, 220)
GOLD       = (255, 200,   0)
LIGHT_BLUE = (140, 210, 240)


# ══════════════════════════════════════════════════════════════════
# ║  1. ABSTRACTION — Abstract Base Class                         ║
# ══════════════════════════════════════════════════════════════════

class GameObject(ABC):
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._alive = True

    @abstractmethod
    def update(self, speed: float) -> None:
        pass

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:         
        pass

    @property
    def alive(self) -> bool:
        return self._alive

    @property
    def x(self) -> float:
        return self._x

    @property
    def y(self) -> float:
        return self._y


class Vehicle(GameObject):
    def __init__(self, x: float, y: float, color: tuple,
                 width: int, height: int):
        super().__init__(x, y)
        self._color  = color
        self._width  = width
        self._height = height

    @abstractmethod
    def on_collision(self) -> None:
        pass

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self._x - self._width  // 2),
            int(self._y - self._height // 2),
            self._width, self._height
        )

    def collides_with(self, other: "Vehicle") -> bool:
        return self.get_rect().inflate(-10, -10).colliderect(
               other.get_rect().inflate(-10, -10))


# ══════════════════════════════════════════════════════════════════
# ║  2. INHERITANCE + 3. ENCAPSULATION                            ║
# ══════════════════════════════════════════════════════════════════

class PlayerCar(Vehicle):
    CAR_W, CAR_H = 42, 72

    def __init__(self, lane: int = 2):
        super().__init__(
            x      = float(LANES[lane]),
            y      = float(SCREEN_H - 130),
            color  = RED,
            width  = self.CAR_W,
            height = self.CAR_H
        )
        self.__lane       = lane
        self.__target_x   = float(LANES[lane])
        self.__score      = 0
        self.__lives      = 3
        self.__invincible = 0
        self.__exhausts   = []
        self.__exhaust_t  = 0

    @property
    def score(self) -> int:
        return self.__score

    @property
    def lives(self) -> int:
        return self.__lives

    @property
    def is_invincible(self) -> bool:
        return self.__invincible > 0

    def add_score(self, pts: int) -> None:
        if pts > 0:
            self.__score += pts

    def set_score(self, val: int) -> None:
        self.__score = max(0, val)

    def move_left(self) -> None:
        if self.__lane > 0:
            self.__lane -= 1
            self.__target_x = float(LANES[self.__lane])

    def move_right(self) -> None:
        if self.__lane < LANE_COUNT - 1:
            self.__lane += 1
            self.__target_x = float(LANES[self.__lane])

    def on_collision(self) -> bool:
        if self.__invincible == 0:
            self.__lives -= 1
            self.__invincible = 90
            return True
        return False

    def update(self, speed: float = 0) -> None:
        dx = self.__target_x - self._x
        self._x += dx * 0.16
        if abs(dx) < 0.5:
            self._x = self.__target_x

        if self.__invincible > 0:
            self.__invincible -= 1

        if self.__exhaust_t % 3 == 0:
            self.__exhausts.append({
                "x": self._x + random.randint(-7, 7),
                "y": self._y + self._height // 2 + 2,
                "r": random.randint(4, 9),
                "life": 22,
                "dx": random.uniform(-0.4, 0.4),
                "dy": random.uniform(1.2, 2.8),
            })
        self.__exhausts = [e for e in self.__exhausts if e["life"] > 0]
        for e in self.__exhausts:
            e["x"] += e["dx"]; e["y"] += e["dy"]
            e["life"] -= 1; e["r"] = max(0, e["r"] - 0.18)

    def draw(self, surface: pygame.Surface) -> None:
        for e in self.__exhausts:
            if e["r"] < 1:
                continue
            alpha = int(160 * e["life"] / 22)
            s = pygame.Surface((int(e["r"])*2+2, int(e["r"])*2+2), pygame.SRCALPHA)
            pygame.draw.circle(s, (170, 170, 170, alpha),
                               (int(e["r"])+1, int(e["r"])+1), int(e["r"]))
            surface.blit(s, (int(e["x"] - e["r"]), int(e["y"] - e["r"])))

        if self.__invincible > 0 and (self.__invincible // 5) % 2 == 1:
            return

        cx, cy = int(self._x), int(self._y)
        w, h   = self._width, self._height

        pygame.draw.rect(surface, RED,
                         (cx-w//2, cy-h//2, w, h), border_radius=9)
        pygame.draw.rect(surface, (230, 230, 230),
                         (cx-4, cy-h//2+12, 8, h-24), border_radius=3)
        pygame.draw.rect(surface, LIGHT_BLUE,
                         (cx-w//2+5, cy-h//2+7, w-10, 18), border_radius=4)
        pygame.draw.rect(surface, LIGHT_BLUE,
                         (cx-w//2+5, cy+h//2-23, w-10, 14), border_radius=3)
        for wx, wy in [(-w//2-5,-h//2+10),(w//2-3,-h//2+10),
                        (-w//2-5, h//2-26),(w//2-3, h//2-26)]:
            pygame.draw.rect(surface, (35,35,35),
                             (cx+wx, cy+wy, 8, 16), border_radius=3)
        pygame.draw.ellipse(surface, YELLOW,
                            (cx-w//2+4, cy-h//2-5, 11, 7))
        pygame.draw.ellipse(surface, YELLOW,
                            (cx+w//2-15, cy-h//2-5, 11, 7))
        pygame.draw.ellipse(surface, (255,80,80),
                            (cx-w//2+4, cy+h//2-4, 11, 7))
        pygame.draw.ellipse(surface, (255,80,80),
                            (cx+w//2-15, cy+h//2-4, 11, 7))
        if 0 < self.__invincible < 30:
            pygame.draw.rect(surface, CYAN,
                             (cx-w//2-4, cy-h//2-4, w+8, h+8),
                             2, border_radius=12)


class EnemyCar(Vehicle):
    def __init__(self, lane: int, game_speed: float,
                 color: tuple, width: int, height: int):
        super().__init__(
            x=float(LANES[lane]), y=float(-height),
            color=color, width=width, height=height
        )
        self._lane      = lane
        self._speed     = game_speed * random.uniform(0.88, 1.14)

    def on_collision(self) -> None:
        self._alive = False

    def update(self, speed: float = 0) -> None:
        self._y += self._speed
        if self._y > SCREEN_H + self._height + 10:
            self._alive = False


class SedanCar(EnemyCar):
    COLORS = [BLUE, GREEN, ORANGE, PURPLE, CYAN, (180,100,60), (60,160,200)]

    def __init__(self, lane: int, game_speed: float):
        super().__init__(lane, game_speed,
                         random.choice(self.COLORS), 42, 72)

    def on_collision(self) -> None:
        self._alive = False

    def update(self, speed: float = 0) -> None:
        self._y += self._speed
        if self._y > SCREEN_H + self._height + 10:
            self._alive = False

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self._x), int(self._y)
        w, h   = self._width, self._height
        pygame.draw.rect(surface, self._color,
                         (cx-w//2, cy-h//2, w, h), border_radius=8)
        pygame.draw.rect(surface, (160,210,245),
                         (cx-w//2+5, cy-h//2+5, w-10, 16), border_radius=4)
        pygame.draw.rect(surface, (160,210,245),
                         (cx-w//2+5, cy+h//2-20, w-10, 12), border_radius=3)
        for wx, wy in [(-w//2-4,-h//2+9),(w//2-4,-h//2+9),
                        (-w//2-4, h//2-23),(w//2-4, h//2-23)]:
            pygame.draw.rect(surface,(35,35,35),(cx+wx,cy+wy,8,14),border_radius=3)
        pygame.draw.ellipse(surface, WHITE, (cx-w//2+4, cy-h//2-4, 10,6))
        pygame.draw.ellipse(surface, WHITE, (cx+w//2-14, cy-h//2-4, 10,6))
        pygame.draw.ellipse(surface, RED, (cx-w//2+4, cy+h//2-3, 10,6))
        pygame.draw.ellipse(surface, RED, (cx+w//2-14, cy+h//2-3, 10,6))


class TruckCar(EnemyCar):
    def __init__(self, lane: int, game_speed: float):
        color = random.choice([(160,80,40),(80,120,160),(100,140,80)])
        super().__init__(lane, game_speed * 0.75, color, 50, 92)

    def on_collision(self) -> None:
        pass

    def update(self, speed: float = 0) -> None:
        self._y += self._speed
        if self._y > SCREEN_H + self._height + 10:
            self._alive = False

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self._x), int(self._y)
        w, h   = self._width, self._height
        dark = tuple(max(0, c-50) for c in self._color)
        pygame.draw.rect(surface, self._color,
                         (cx-w//2, cy-h//2+h//3, w, h-h//3), border_radius=5)
        pygame.draw.rect(surface, dark,
                         (cx-w//2+3, cy-h//2, w-6, h//3+6), border_radius=6)
        pygame.draw.rect(surface, LIGHT_BLUE,
                         (cx-w//2+7, cy-h//2+5, w-14, 14), border_radius=3)
        for wx, wy in [(-w//2-5,-h//2+12),(w//2-3,-h//2+12),
                        (-w//2-5, h//2-30),(w//2-3, h//2-30),
                        (-w//2-5, h//2-16),(w//2-3, h//2-16)]:
            pygame.draw.rect(surface,(35,35,35),(cx+wx,cy+wy,8,14),border_radius=3)
        pygame.draw.ellipse(surface, YELLOW, (cx-w//2+5, cy-h//2-4, 12,7))
        pygame.draw.ellipse(surface, YELLOW, (cx+w//2-17, cy-h//2-4, 12,7))
        for gy in range(int(cy - h//2 + h//3 + 10), int(cy + h//2 - 8), 12):
            pygame.draw.line(surface, dark, (cx-w//2+3, gy), (cx+w//2-3, gy), 1)


class SportCar(EnemyCar):
    def __init__(self, lane: int, game_speed: float):
        color = random.choice([(220,220,20),(200,50,200),(20,200,200)])
        super().__init__(lane, game_speed * 1.25, color, 38, 65)

    def on_collision(self) -> None:
        self._alive = False

    def update(self, speed: float = 0) -> None:
        self._y += self._speed
        if self._y > SCREEN_H + self._height + 10:
            self._alive = False

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self._x), int(self._y)
        w, h   = self._width, self._height
        pygame.draw.rect(surface, self._color,
                         (cx-w//2, cy-h//2, w, h), border_radius=10)
        pygame.draw.rect(surface, BLACK,
                         (cx-3, cy-h//2+8, 6, h-16), border_radius=2)
        pygame.draw.rect(surface, (180,230,255),
                         (cx-w//2+4, cy-h//2+6, w-8, 14), border_radius=4)
        for wx, wy in [(-w//2-4,-h//2+8),(w//2-4,-h//2+8),
                        (-w//2-4, h//2-20),(w//2-4, h//2-20)]:
            pygame.draw.rect(surface,(35,35,35),(cx+wx,cy+wy,8,12),border_radius=3)
        pygame.draw.rect(surface, BLACK,
                         (cx-w//2-2, cy+h//2-8, w+4, 5), border_radius=2)
        pygame.draw.line(surface, (200,255,200),
                         (cx-w//2+3, cy-h//2-2), (cx+w//2-3, cy-h//2-2), 3)


# ══════════════════════════════════════════════════════════════════
# ║  ABSTRACTION + POLYMORPHISM — Collectible items               ║
# ══════════════════════════════════════════════════════════════════

class Collectible(GameObject):
    def __init__(self, lane: int):
        super().__init__(float(LANES[lane]), float(-20))
        self.__collected = False

    @property
    def collected(self) -> bool:
        return self.__collected

    def collect(self) -> None:
        self.__collected = True
        self._alive = False

    def is_near(self, player: PlayerCar, radius: int) -> bool:
        dist = math.hypot(self._x - player.x, self._y - player.y)
        return dist < radius

    @abstractmethod
    def get_value(self) -> int:
        pass

    def update(self, speed: float) -> None:
        self._y += speed
        if self._y > SCREEN_H + 30:
            self._alive = False


class CoinItem(Collectible):
    def __init__(self, lane: int):
        super().__init__(lane)
        self.__angle = 0.0
        self.__r     = 13

    def get_value(self) -> int:
        return 10

    def update(self, speed: float) -> None:
        super().update(speed)
        self.__angle = (self.__angle + 4) % 360

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self._x), int(self._y)
        scale  = max(0.15, abs(math.cos(math.radians(self.__angle))))
        ew     = max(3, int(self.__r * 2 * scale))
        pygame.draw.ellipse(surface, GOLD,
                            (cx-ew//2, cy-self.__r, ew, self.__r*2))
        pygame.draw.ellipse(surface, (255,240,120),
                            (cx-ew//2+1, cy-self.__r+3, max(2,ew-3), self.__r*2-6))
        pygame.draw.ellipse(surface, (200,160,0),
                            (cx-ew//2, cy-self.__r, ew, self.__r*2), 2)


class StarItem(Collectible):
    def __init__(self, lane: int):
        super().__init__(lane)
        self.__pulse = 0

    def get_value(self) -> int:
        return 50

    def update(self, speed: float) -> None:
        super().update(speed)
        self.__pulse = (self.__pulse + 5) % 360

    def draw(self, surface: pygame.Surface) -> None:
        cx, cy = int(self._x), int(self._y)
        r  = 14 + int(3 * math.sin(math.radians(self.__pulse)))
        ir = r // 2
        pts = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            radius = r if i % 2 == 0 else ir
            pts.append((cx + radius * math.cos(angle),
                         cy + radius * math.sin(angle)))
        pygame.draw.polygon(surface, YELLOW, pts)
        pygame.draw.polygon(surface, (255,255,100), pts, 2)


# ══════════════════════════════════════════════════════════════════
# ║  Particle — efek visual                                       ║
# ══════════════════════════════════════════════════════════════════

class Particle(GameObject):
    def __init__(self, x: float, y: float, color: tuple):
        super().__init__(x, y)
        ang      = random.uniform(0, math.pi * 2)
        spd      = random.uniform(2, 7)
        self.__vx    = math.cos(ang) * spd
        self.__vy    = math.sin(ang) * spd - 1.5
        self.__r     = random.uniform(3, 8)
        self.__life  = random.randint(22, 40)
        self.__maxl  = self.__life
        self.__color = color

    def update(self, speed: float = 0) -> None:
        self._x     += self.__vx
        self._y     += self.__vy
        self.__vy   += 0.18
        self.__life -= 1
        self.__r     = max(0, self.__r - 0.12)
        if self.__life <= 0:
            self._alive = False

    def draw(self, surface: pygame.Surface) -> None:
        if self.__life <= 0 or self.__r < 1:
            return
        alpha = int(255 * self.__life / self.__maxl)
        r     = int(self.__r)
        s = pygame.Surface((r*2+2, r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.__color, alpha), (r+1, r+1), r)
        surface.blit(s, (int(self._x - r), int(self._y - r)))


# ══════════════════════════════════════════════════════════════════
# ║  Track — rendering jalan                                       ║
# ══════════════════════════════════════════════════════════════════

class Track(GameObject):
    def __init__(self):
        super().__init__(0, 0)
        self.__road_y = 0.0
        self.__trees  = [{"x": random.choice([20,35,550,570]),
                           "y": float(random.randint(0,SCREEN_H)),
                           "sz": random.randint(14,22)} for _ in range(12)]
        self.__lines_y = 0.0

    def update(self, speed: float) -> None:
        self.__road_y   += speed
        self.__lines_y  += speed
        for t in self.__trees:
            t["y"] += speed * 0.75
            if t["y"] > SCREEN_H + 30:
                t["y"] = -30
                t["sz"] = random.randint(14, 22)

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(GRASS_COL)
        pygame.draw.rect(surface, ROAD_COL,
                         (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_H))
        dh, dg = 38, 28
        period = dh + dg
        for lx in [ROAD_LEFT + LANE_W * i for i in range(1, LANE_COUNT)]:
            offset = int(self.__lines_y) % period
            y = -period + offset
            while y < SCREEN_H + period:
                pygame.draw.rect(surface, DASH_COL, (lx-2, y, 4, dh))
                y += period
        pygame.draw.rect(surface, WHITE, (ROAD_LEFT-3, 0, 3, SCREEN_H))
        pygame.draw.rect(surface, WHITE, (ROAD_RIGHT,  0, 3, SCREEN_H))
        for t in self.__trees:
            tx, ty, sz = int(t["x"]), int(t["y"]), t["sz"]
            pygame.draw.rect(surface, (90,60,30), (tx-3, ty, 6, sz//2))
            pygame.draw.circle(surface, (30,120,30), (tx, ty), sz)
            pygame.draw.circle(surface, (50,160,50), (tx-3, ty-4), sz//2)


# ══════════════════════════════════════════════════════════════════
# ║  EnemyFactory — Factory Pattern                               ║
# ══════════════════════════════════════════════════════════════════

class EnemyFactory:
    @staticmethod
    def create(lane: int, game_speed: float) -> EnemyCar:
        kinds = [SedanCar, SedanCar, SedanCar, TruckCar, SportCar]
        cls   = random.choice(kinds)
        return cls(lane, game_speed)


# ══════════════════════════════════════════════════════════════════
# ║  Game — Controller Utama                                      ║
# ══════════════════════════════════════════════════════════════════

class Game:
    def __init__(self):
        self.__screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Game Balap Mobil — 4 Pilar OOP")
        self.__clock   = pygame.time.Clock()

        self.__font_xl  = pygame.font.SysFont("arial", 44, bold=True)
        self.__font_lg  = pygame.font.SysFont("arial", 26, bold=True)
        self.__font_md  = pygame.font.SysFont("arial", 18, bold=True)
        self.__font_sm  = pygame.font.SysFont("arial", 14)
        self.__font_hud = pygame.font.SysFont("monospace", 19, bold=True)
        self.__font_count = pygame.font.SysFont("arial", 120, bold=True)  # Font untuk hitungan

        self.__best     = 0
        self.__reset()

    def __reset(self):
        self.__track      = Track()
        self.__player     = PlayerCar(lane=2)

        self.__enemies    : list[EnemyCar]    = []
        self.__items      : list[Collectible] = []
        self.__particles  : list[Particle]    = []

        self.__speed       = 4.2
        self.__elapsed     = 0
        self.__spawn_t     = 0
        self.__item_t      = 0
        self.__spawn_int   = 75
        self.__shake       = 0
        self.__phase       = "start"
        
        # ── FITUR HITUNGAN 3-2-1-GO ──────────────────────────────
        self.__countdown   = 3      # Mulai dari angka 3
        self.__countdown_timer = 0   # Timer untuk hitungan
        self.__countdown_active = False

    def __start_countdown(self):
        """Memulai hitungan 3-2-1-GO sebelum game dimulai"""
        self.__countdown = 3
        self.__countdown_active = True
        self.__countdown_timer = pygame.time.get_ticks()  # Catat waktu mulai

    def __spawn_enemy(self):
        used = {e._lane for e in self.__enemies if e._y < 0}
        avail = [l for l in range(LANE_COUNT) if l not in used]
        if not avail:
            return
        e = EnemyFactory.create(random.choice(avail), self.__speed)
        self.__enemies.append(e)

    def __spawn_item(self):
        lane = random.randint(0, LANE_COUNT-1)
        item = StarItem(lane) if random.random() < 0.2 else CoinItem(lane)
        self.__items.append(item)

    def __add_particles(self, x: float, y: float, color: tuple, n: int = 14):
        for _ in range(n):
            self.__particles.append(Particle(x, y, color))

    def __handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.__phase in ("start", "over"):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.__reset()
                        self.__start_countdown()  # Mulai hitungan
                        self.__phase = "countdown"  # Pindah ke mode countdown
                elif self.__phase == "play":
                    if event.key in (pygame.K_LEFT,  pygame.K_a):
                        self.__player.move_left()
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.__player.move_right()
        return True

    def __update(self):
        self.__elapsed += 1
        self.__speed    = min(4.2 + (self.__elapsed // 280) * 0.45, 13.0)
        self.__spawn_int = max(32, 75 - (self.__elapsed // 240) * 6)

        # POLYMORPHISM: track.update() → player.update() → enemy.update()
        self.__track.update(self.__speed)
        self.__player.update()
        self.__player.set_score(self.__elapsed // 4)

        # Collision avoidance system
        enemies_by_lane = {}
        for e in self.__enemies:
            if e._lane not in enemies_by_lane:
                enemies_by_lane[e._lane] = []
            enemies_by_lane[e._lane].append(e)
        
        for lane, enemies in enemies_by_lane.items():
            enemies.sort(key=lambda x: x._y)
            for i in range(len(enemies) - 1):
                current = enemies[i]
                next_enemy = enemies[i + 1]
                if next_enemy._y - current._y < 60:
                    if current._y < next_enemy._y:
                        current._speed = min(current._speed, next_enemy._speed * 0.95)
                    else:
                        next_enemy._speed = min(next_enemy._speed, current._speed * 0.95)

        self.__spawn_t += 1
        if self.__spawn_t >= self.__spawn_int:
            self.__spawn_enemy(); self.__spawn_t = 0
        self.__item_t += 1
        if self.__item_t >= 85:
            self.__spawn_item(); self.__item_t = 0

        for e in self.__enemies:
            e.update(self.__speed)
            if not self.__player.is_invincible:
                if self.__player.collides_with(e):
                    e.on_collision()
                    hit = self.__player.on_collision()
                    if hit:
                        self.__add_particles(self.__player.x, self.__player.y, RED, 16)
                        self.__add_particles(e.x, e.y, e._color, 10)
                        self.__shake = 22
                        if self.__player.lives <= 0:
                            self.__phase = "over"
                            if self.__player.score > self.__best:
                                self.__best = self.__player.score

        self.__enemies = [e for e in self.__enemies if e.alive]

        for it in self.__items:
            it.update(self.__speed * 0.9)
            if it.alive and it.is_near(self.__player, 22):
                pts = it.get_value()
                it.collect()
                self.__player.add_score(pts)
                self.__add_particles(it.x, it.y, GOLD, 8)

        self.__items = [it for it in self.__items if it.alive]

        for p in self.__particles:
            p.update()
        self.__particles = [p for p in self.__particles if p.alive]

        if self.__shake > 0:
            self.__shake -= 1

    def __update_countdown(self):
        """Update logika hitungan 3-2-1-GO"""
        if not self.__countdown_active:
            return
        
        now = pygame.time.get_ticks()
        elapsed = now - self.__countdown_timer
        
        # Ganti angka setiap 1 detik (1000 ms)
        if elapsed >= 4000:  # Setelah 4 detik (3,2,1,GO)
            self.__countdown_active = False
            self.__phase = "play"  # Mulai game
        elif elapsed >= 3000:
            self.__countdown = "GO!"
        elif elapsed >= 2000:
            self.__countdown = 1
        elif elapsed >= 1000:
            self.__countdown = 2
        else:
            self.__countdown = 3

    def __draw_hud(self):
        hud = pygame.Surface((SCREEN_W, 58), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 150))
        self.__screen.blit(hud, (0, 0))

        sc  = self.__font_hud.render(f"SKOR : {self.__player.score}", True, WHITE)
        km  = int(80 + self.__speed * 8)
        sp  = self.__font_hud.render(f"{km} km/h", True, YELLOW)
        bs  = self.__font_hud.render(f"BEST : {self.__best}", True, GOLD)
        lvl = self.__font_sm.render(
              f"Lv.{1 + self.__elapsed//280}  |  Sedan · Truk · Sport", True, (180,220,180))

        self.__screen.blit(sc,  (12, 8))
        self.__screen.blit(sp,  (SCREEN_W//2 - sp.get_width()//2, 8))
        self.__screen.blit(bs,  (SCREEN_W - bs.get_width() - 12, 8))
        self.__screen.blit(lvl, (SCREEN_W//2 - lvl.get_width()//2, 34))

        for i in range(3):
            col = RED if i < self.__player.lives else GRAY
            hx  = 12 + i * 26
            hy  = 34
            pygame.draw.circle(self.__screen, col, (hx+5, hy+5), 5)
            pygame.draw.circle(self.__screen, col, (hx+14,hy+5), 5)
            pygame.draw.polygon(self.__screen, col,
                                [(hx,hy+8),(hx+9,hy+18),(hx+19,hy+8)])

    def __draw_countdown(self):
        """Menggambar hitungan 3-2-1-GO di tengah layar"""
        if not self.__countdown_active:
            return
        
        # Buat teks dengan efek transparan
        text = str(self.__countdown)
        color = YELLOW if text == "GO!" else (255, 255, 255)
        
        # Efek membesar (scale effect)
        now = pygame.time.get_ticks()
        elapsed = now - self.__countdown_timer
        frame = elapsed % 1000
        scale = 1.0 + (1.0 - frame / 1000) * 0.5  # Membesar lalu mengecil
        
        if text == "GO!":
            color = GREEN
            text_surface = self.__font_count.render(text, True, color)
        else:
            text_surface = self.__font_count.render(text, True, color)
        
        # Posisi di tengah layar
        text_rect = text_surface.get_rect(center=(SCREEN_W//2, SCREEN_H//2))
        
        # Efek shadow
        shadow_surface = self.__font_count.render(text, True, BLACK)
        shadow_rect = shadow_surface.get_rect(center=(SCREEN_W//2 + 5, SCREEN_H//2 + 5))
        self.__screen.blit(shadow_surface, shadow_rect)
        
        # Gambar teks utama
        self.__screen.blit(text_surface, text_rect)
        
        # Tambahan efek lingkaran di sekitar angka
        if text != "GO!":
            alpha = int(255 * (1 - frame / 1000))
            circle_surf = pygame.Surface((150, 150), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (*color, alpha), (75, 75), 60, 5)
            self.__screen.blit(circle_surf, (SCREEN_W//2 - 75, SCREEN_H//2 - 75))

    def __draw_overlay(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0,0,0,165))
        self.__screen.blit(ov, (0,0))

        lines = []
        if self.__phase == "start":
            lines = [
                (self.__font_xl,  "GAME BALAP MOBIL", YELLOW),
                (self.__font_lg,  "4 Pilar OOP Python", (200,200,200)),
                (self.__font_md,  "", WHITE),
                (self.__font_md,  "ABSTRACTION   - GameObject & Vehicle", (150,220,255)),
                (self.__font_md,  "INHERITANCE   - Car -> Sedan/Truk/Sport", (150,255,180)),
                (self.__font_md,  "ENCAPSULATION - __score, __lives privat", (255,220,150)),
                (self.__font_md,  "POLYMORPHISM  - draw() & update() beda", (255,160,160)),
                (self.__font_md,  "", WHITE),
                (self.__font_lg,  "← A  Kiri   |   D →  Kanan", WHITE),
                (self.__font_lg,  "SPACE / ENTER  =  Mulai", (180,255,180)),
            ]
        elif self.__phase == "over":
            nb = self.__player.score >= self.__best
            lines = [
                (self.__font_xl, "GAME OVER!", RED),
                (self.__font_lg, f"Skor: {self.__player.score}", WHITE),
                (self.__font_lg, f"Terbaik: {self.__best}", GOLD),
            ]
            if nb:
                lines.append((self.__font_lg, "REKOR BARU!", YELLOW))
            lines.append((self.__font_lg, "SPACE / ENTER = Main Lagi", (180,255,180)))

        cy = SCREEN_H // 2 - (len(lines) * 30) // 2
        for font, text, color in lines:
            s = font.render(text, True, color)
            self.__screen.blit(s, (SCREEN_W//2 - s.get_width()//2, cy))
            cy += s.get_height() + 8

    def __draw(self):
        ox = random.randint(-5,5) if self.__shake > 0 else 0
        oy = random.randint(-4,4) if self.__shake > 0 else 0

        buf = pygame.Surface((SCREEN_W, SCREEN_H))

        self.__track.draw(buf)

        for it in self.__items:
            it.draw(buf)

        for e in self.__enemies:
            e.draw(buf)

        self.__player.draw(buf)

        for p in self.__particles:
            p.draw(buf)

        self.__screen.blit(buf, (ox, oy))
        self.__draw_hud()
        
        # Gambar hitungan jika sedang aktif
        if self.__phase == "countdown":
            self.__draw_countdown()
        
        if self.__phase in ("start", "over"):
            self.__draw_overlay()

    def run(self):
        running = True
        while running:
            self.__clock.tick(FPS)
            running = self.__handle_events()
            
            if self.__phase == "play":
                self.__update()
            elif self.__phase == "countdown":
                self.__update_countdown()  # Update hitungan 3-2-1-GO
                # Selama countdown, track tetap berjalan tapi mobil tidak bergerak
                self.__track.update(0)  # Track diam selama countdown
            
            self.__draw()
            pygame.display.flip()
        
        pygame.quit()
        sys.exit()


# ── Entry point ─────────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()