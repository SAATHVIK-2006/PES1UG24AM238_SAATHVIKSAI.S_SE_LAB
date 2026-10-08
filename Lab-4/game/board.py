import random
import math
import pygame

GRID_SIZE = 8
TILE_SIZE = 60
GEM_COLORS = [
    (220, 50, 50),   # Red
    (50, 200, 50),   # Green
    (50, 100, 240),  # Blue
    (240, 200, 40),  # Yellow
    (180, 50, 220),  # Purple
    (240, 130, 40),  # Orange
]


class Gem:
    def __init__(self, color, target_row, col, special=None):
        self.color = color
        self.target_row = target_row
        self.col = col
        self.current_y = (target_row - 2) * TILE_SIZE
        self.target_y = target_row * TILE_SIZE
        self.fall_speed = 12.0
        self.special = special  # None, 'row', or 'col'

    def update(self):
        if self.current_y < self.target_y:
            self.current_y += self.fall_speed
            if self.current_y > self.target_y:
                self.current_y = self.target_y

    def is_animating(self):
        return self.current_y < self.target_y


class Board:

    def __init__(self, offset_x, offset_y, target_score=500, max_moves=20):
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.target_score = target_score
        self.max_moves = max_moves
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.selected = None
        self.last_swap = None
        self.is_initializing = False
        self.last_action_time = pygame.time.get_ticks()
        self.score = 0
        self.moves_remaining = max_moves
        self.reset()

    def reset(self):
        self.score = 0
        self.moves_remaining = self.max_moves
        self.selected = None
        self.last_swap = None
        self.last_action_time = pygame.time.get_ticks()
        self.is_initializing = True
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                self.grid[r][c] = Gem(random.choice(GEM_COLORS), r, c)

        self.resolve_matches()
        self.is_initializing = False

    def is_animating(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c] and self.grid[r][c].is_animating():
                    return True
        return False

    def reset_idle_timer(self):
        self.last_action_time = pygame.time.get_ticks()

    def find_possible_move(self):
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                for dr, dc in [(0, 1), (1, 0)]:
                    nr, nc = r + dr, c + dc
                    if nr < GRID_SIZE and nc < GRID_SIZE:
                        if self.grid[r][c] is None or self.grid[nr][nc] is None:
                            continue
                        self.grid[r][c], self.grid[nr][nc] = (
                            self.grid[nr][nc],
                            self.grid[r][c],
                        )
                        matches = self.find_matches()
                        self.grid[r][c], self.grid[nr][nc] = (
                            self.grid[nr][nc],
                            self.grid[r][c],
                        )

                        if matches:
                            return ((r, c), (nr, nc))
        return None

    def swap_gems(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2

        g1, g2 = self.grid[r1][c1], self.grid[r2][c2]
        self.grid[r1][c1], self.grid[r2][c2] = g2, g1

        if self.grid[r1][c1]:
            self.grid[r1][c1].target_row = r1
            self.grid[r1][c1].target_y = r1 * TILE_SIZE
            self.grid[r1][c1].current_y = r1 * TILE_SIZE

        if self.grid[r2][c2]:
            self.grid[r2][c2].target_row = r2
            self.grid[r2][c2].target_y = r2 * TILE_SIZE
            self.grid[r2][c2].current_y = r2 * TILE_SIZE

    def is_adjacent(self, pos1, pos2):
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2) == 1

    def find_matches_and_specials(self):
        matched = set()
        specials_to_create = []

        for r in range(GRID_SIZE):
            c = 0
            while c < GRID_SIZE:
                gem = self.grid[r][c]
                if not gem:
                    c += 1
                    continue
                color = gem.color
                run = [(r, c)]
                k = c + 1
                while k < GRID_SIZE and self.grid[r][k] and self.grid[r][k].color == color:
                    run.append((r, k))
                    k += 1

                if len(run) >= 3:
                    matched.update(run)
                    if len(run) >= 4 and not self.is_initializing:
                        pivot = run[len(run) // 2]
                        if self.last_swap:
                            for swap_pos in self.last_swap:
                                if swap_pos in run:
                                    pivot = swap_pos
                                    break
                        specials_to_create.append((pivot[0], pivot[1], color, 'row'))
                c = k

        for c in range(GRID_SIZE):
            r = 0
            while r < GRID_SIZE:
                gem = self.grid[r][c]
                if not gem:
                    r += 1
                    continue
                color = gem.color
                run = [(r, c)]
                k = r + 1
                while k < GRID_SIZE and self.grid[k][c] and self.grid[k][c].color == color:
                    run.append((k, c))
                    k += 1

                if len(run) >= 3:
                    matched.update(run)
                    if len(run) >= 4 and not self.is_initializing:
                        pivot = run[len(run) // 2]
                        if self.last_swap:
                            for swap_pos in self.last_swap:
                                if swap_pos in run:
                                    pivot = swap_pos
                                    break
                        specials_to_create.append((pivot[0], pivot[1], color, 'col'))
                r = k

        detonated = set(matched)
        queue = list(matched)
        while queue:
            qr, qc = queue.pop(0)
            q_gem = self.grid[qr][qc]
            if q_gem and q_gem.special:
                if q_gem.special == 'row':
                    for ci in range(GRID_SIZE):
                        if (qr, ci) not in detonated and self.grid[qr][ci]:
                            detonated.add((qr, ci))
                            queue.append((qr, ci))
                elif q_gem.special == 'col':
                    for ri in range(GRID_SIZE):
                        if (ri, qc) not in detonated and self.grid[ri][qc]:
                            detonated.add((ri, qc))
                            queue.append((ri, qc))

        return detonated, specials_to_create

    def find_matches(self):
        matches, _ = self.find_matches_and_specials()
        return matches

    def resolve_matches(self):
        total_points = 0
        combo = 1

        while True:
            matches, specials_to_create = self.find_matches_and_specials()
            if not matches:
                break

            wave_cleared = len(matches)
            total_points += wave_cleared * 10 * combo
            combo += 1

            for r, c in matches:
                self.grid[r][c] = None

            for r, c, color, spec_type in specials_to_create:
                new_gem = Gem(color, r, c, special=spec_type)
                new_gem.current_y = r * TILE_SIZE
                self.grid[r][c] = new_gem

            self.drop_and_refill()

        return total_points

    def process_swap(self, pos1, pos2):
        if not self.is_adjacent(pos1, pos2) or self.is_game_over() or self.is_animating():
            return False

        self.last_swap = (pos1, pos2)
        self.swap_gems(pos1, pos2)
        matches = self.find_matches()

        if not matches:
            self.swap_gems(pos1, pos2)
            self.last_swap = None
            return False

        self.moves_remaining -= 1
        points_earned = self.resolve_matches()
        self.score += points_earned
        self.last_swap = None
        return True

    def drop_and_refill(self):
        for c in range(GRID_SIZE):
            empty_slots = 0
            for r in range(GRID_SIZE - 1, -1, -1):
                if self.grid[r][c] is None:
                    empty_slots += 1
                elif empty_slots > 0:
                    gem = self.grid[r][c]
                    gem.target_row = r + empty_slots
                    gem.target_y = (r + empty_slots) * TILE_SIZE
                    self.grid[r + empty_slots][c] = gem
                    self.grid[r][c] = None

            for r in range(empty_slots):
                color = random.choice(GEM_COLORS)
                new_gem = Gem(color, r, c)
                new_gem.current_y = (r - empty_slots) * TILE_SIZE
                self.grid[r][c] = new_gem

    def is_game_over(self):
        return self.score >= self.target_score or self.moves_remaining <= 0

    def check_result(self):
        if self.score >= self.target_score:
            return "WIN"
        if self.moves_remaining <= 0:
            return "LOSS"
        return None

    def update(self):
        animating = False
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                if self.grid[r][c]:
                    self.grid[r][c].update()
                    if self.grid[r][c].is_animating():
                        animating = True

        if animating or self.selected is not None or self.is_game_over():
            self.reset_idle_timer()

    def render(self, surface):
        board_rect = pygame.Rect(
            self.offset_x, self.offset_y, GRID_SIZE * TILE_SIZE, GRID_SIZE * TILE_SIZE
        )
        pygame.draw.rect(surface, (20, 22, 28), board_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 65, 75), board_rect, width=3, border_radius=8)

        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                gem = self.grid[r][c]
                if gem:
                    x = self.offset_x + c * TILE_SIZE
                    y = self.offset_y + gem.current_y
                    tile_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)

                    pygame.draw.rect(surface, gem.color, tile_rect, border_radius=10)
                    pygame.draw.rect(
                        surface, (255, 255, 255), tile_rect, width=1, border_radius=10
                    )

                    if gem.special:
                        pulse = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.008))
                        glow_color = (255, 255, max(0, min(255, pulse)))
                        pygame.draw.rect(surface, glow_color, tile_rect, width=3, border_radius=10)

                        cx, cy = tile_rect.centerx, tile_rect.centery
                        if gem.special == 'row':
                            pygame.draw.line(surface, (255, 255, 255), (tile_rect.left + 8, cy), (tile_rect.right - 8, cy), 4)
                        elif gem.special == 'col':
                            pygame.draw.line(surface, (255, 255, 255), (cx, tile_rect.top + 8), (cx, tile_rect.bottom - 8), 4)
                        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 5)

                if self.selected == (r, c):
                    sel_x = self.offset_x + c * TILE_SIZE
                    sel_y = self.offset_y + r * TILE_SIZE
                    sel_rect = pygame.Rect(sel_x + 2, sel_y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(
                        surface, (255, 255, 255), sel_rect, width=4, border_radius=10
                    )

        now = pygame.time.get_ticks()
        if (
            now - self.last_action_time >= 5000
            and not self.is_animating()
            and not self.is_game_over()
        ):
            hint_pair = self.find_possible_move()
            if hint_pair:
                pulse = int(160 + 95 * math.sin(now * 0.007))
                hint_color = (255, max(80, min(255, pulse)), 40)
                for hr, hc in hint_pair:
                    hx = self.offset_x + hc * TILE_SIZE
                    hy = self.offset_y + hr * TILE_SIZE
                    hint_rect = pygame.Rect(hx + 2, hy + 2, TILE_SIZE - 4, TILE_SIZE - 4)
                    pygame.draw.rect(
                        surface, hint_color, hint_rect, width=3, border_radius=10
                    )
