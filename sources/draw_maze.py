from __future__ import annotations
from sources.draw_path import calcul_path_coordinates, find_path
from sources.maze_generator import MazeGenerator
import sys
import os
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pygame.sprite
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

try:
    import pygame
except ModuleNotFoundError:
    print("ERROR: can't use pygame")
    exit(1)


class Player(pygame.sprite.Sprite):
    def __init__(self, start: tuple[int, int], width: int, height: int,
                 cell: int) -> None:
        super().__init__()
        px = start[0] * cell + cell + cell// 2
        py = start[1] * cell + cell + cell// 2
        if cell == 20:
            player_size = cell / 2
        elif cell == 10:
            player_size = cell / 2
        else:
            player_size = cell / 2
        self.image = pygame.Surface((player_size, player_size))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=(px, py))
        self.vel = pygame.Vector2(0, 0)
        self.score = 0
        self.width = width
        self.height = height

    def update(self, walls_group: pygame.sprite.Group[Any]) -> None:
        keys = pygame.key.get_pressed()
        self.vel.x = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * 4
        self.vel.y = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * 4

        self.rect.x += int(self.vel.x)
        hits = pygame.sprite.spritecollide(self, walls_group, False)
        for hit in hits:
            if self.vel.x > 0:
                self.rect.right = hit.rect.left
            elif self.vel.x < 0:
                self.rect.left = hit.rect.right

        self.rect.y += int(self.vel.y)
        hits = pygame.sprite.spritecollide(self, walls_group, False)
        for hit in hits:
            if self.vel.y > 0:
                self.rect.bottom = hit.rect.top
            elif self.vel.y < 0:
                self.rect.top = hit.rect.bottom


class End(pygame.sprite.Sprite):
    def __init__(self, end: tuple[int, int], cell: int) -> None:
        super().__init__()
        px = end[0] * cell + cell + cell // 2
        py = end[1] * cell + cell + cell // 2
        self.image = pygame.Surface((cell - 4, cell - 4))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(px, py))
        self.vel = pygame.Vector2(0, 0)
        self.score = 0


class Wall(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, w: int, h: int) -> None:
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(topleft=(x, y))


WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (50, 50, 255)
YELLOW = (255, 215, 0)
PINK = (255, 180, 180)
PURPLE = (153, 50, 204)
BROWN = (139, 69, 25)
GOLD = (184, 134, 11)
GRAY = (169, 169, 169)
BLACK = (0, 0, 0)


def run_maze(hexa: str, w: int, h: int) -> list[dict[str, int]]:
    north = ["1", "3", "5", "7", "9", "B", "D", "F"]
    south = ["4", "5", "6", "7", "C", "D", "E", "F"]
    est = ["2", "3", "6", "7", "A", "B", "E", "F"]
    west = ["8", "9", "A", "B", "C", "D", "E", "F"]
    cell_walls: list[dict[str, int]] = []
    for c in hexa:
        if len(cell_walls) >= w * h:
            break
        if not c or c == "\n":
            continue
        if c not in "0123456789ABCDEF":
            break
        walls = {"N": 0, "S": 0, "E": 0, "W": 0}
        if c in north:
            walls["N"] = 1
        if c in south:
            walls["S"] = 1
        if c in est:
            walls["E"] = 1
        if c in west:
            walls["W"] = 1
        cell_walls.append(walls)
    return cell_walls


def print_walls(cell_walls: list[dict[str, int]], width: int, height: int,
                cell: int, screen: pygame.Surface, x: int, y: int, x1: int,
                y1: int, x2: int, y2: int, color_ft: list[tuple[int, int]],
                color: tuple[int, int, int]) -> None:
    idx = 0
    for y0 in range(height):
        for x0 in range(width):
            cell_x = x + x0 * cell + cell
            cell_y = y + y0 * cell + cell

            if x0 % 2 != 0 and y0 % 2 != 0:
                pygame.draw.rect(screen, color, (cell_x, cell_y, cell, cell))

            if x0 % 2 == 0 and y0 % 2 == 0:
                if cell_walls[idx].get("S") == 1 and y0 + 1 < height:
                    pygame.draw.rect(screen, color, (cell_x, cell_y + cell,
                                                     cell, cell))
                if cell_walls[idx].get("E") == 1 and x0 + 1 < width:
                    pygame.draw.rect(screen, color, (cell_x + cell, cell_y,
                                                     cell, cell))
                idx += 1

            if (x0, y0) in color_ft:
                pygame.draw.rect(screen, BLUE, (cell_x - cell, cell_y - cell,
                                                cell, cell))
            if x0 == x1 and y0 == y1:
                pygame.draw.rect(screen, GREEN, (cell_x, cell_y, cell, cell))
            if x0 == x2 and y0 == y2:
                pygame.draw.rect(screen, RED, (cell_x, cell_y, cell, cell))
                idx += 1


def print_path(cell_walls: list[dict[str, int]], width: int, height: int,
               cell: int, screen: pygame.Surface, x: int, y: int, x1: int,
               y1: int, x2: int, y2: int, color_ft: list[tuple[int, int]],
               path_coordinates: list[tuple[int, int]],
               color: tuple[int, int, int]) -> None:
    print_walls(cell_walls, width, height, cell, screen, x, y, x1, y1, x2, y2,
                color_ft, color)
    for y0 in range(height):
        for x0 in range(width):
            cell_x = x + x0 * cell + cell
            cell_y = y + y0 * cell + cell
            if (x0, y0) in path_coordinates:
                pygame.draw.rect(screen, GREEN, (cell_x, cell_y,
                                                 cell, cell))


def rm_path(cell_walls: list[dict[str, int]], width: int, height: int,
               cell: int, screen: pygame.Surface, x: int, y: int, x1: int,
               y1: int, x2: int, y2: int, color_ft: list[tuple[int, int]],
               path_coordinates: list[tuple[int, int]],
               color: tuple[int, int, int]) -> None:
    print_walls(cell_walls, width, height, cell, screen, x, y, x1, y1, x2, y2,
                color_ft, color)
    for y0 in range(height):
        for x0 in range(width):
            cell_x = x + x0 * cell + cell
            cell_y = y + y0 * cell + cell
            if (x0, y0) in path_coordinates:
                pygame.draw.rect(screen, BLACK, (cell_x, cell_y,
                                                 cell, cell))


def change_mouse_cursor(surf1: pygame.rect.Rect, surf2: pygame.rect.Rect,
                        surf3: pygame.rect.Rect, surf4: pygame.rect.Rect,
                        surf0: pygame.rect.Rect, surf5: pygame.rect.Rect,
                        surf6: pygame.rect.Rect) -> tuple[int, int]:
    mouse_pos = pygame.mouse.get_pos()
    if surf1.collidepoint(mouse_pos) or surf2.collidepoint(mouse_pos)\
        or surf3.collidepoint(mouse_pos) or surf4.collidepoint(mouse_pos)\
            or surf5.collidepoint(mouse_pos) or surf0.collidepoint(mouse_pos)\
            or surf6.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    return mouse_pos


def hide_path(surf_lst: list[pygame.Surface],
              screen: pygame.Surface, font: pygame.font.Font,
              color: list[tuple[int, int, int]],
              lines: list[str], maze_bottom: int) -> None:
    rect_txt = surf_lst[2].get_rect(topleft=(0, maze_bottom + 35*2))
    pygame.draw.rect(screen, (0, 0, 0), rect_txt)
    font.render("Hide path", True, color)
    lines[2] = "2- Hide path"


def show_the_path(surf_lst: list[pygame.Surface],
                  screen: pygame.Surface, font: pygame.font.Font,
                  color: list[tuple[int, int, int]],
                  lines: list[str], maze_bottom: int) -> None:
    rect_txt = surf_lst[2].get_rect(topleft=(0, maze_bottom + 35*2))
    pygame.draw.rect(screen, (0, 0, 0), rect_txt)
    lines[2] = "2- Show path from entry to exit"
    font.render(lines[2], True, color)


def easter_egg() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(base_dir, "..", "resources", "amongus.wav")
    sound = pygame.mixer.Sound(sound_path)
    sound.set_volume(1.0)
    sound.play()


def play_sound() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sound_path = os.path.join(base_dir, "..", "resources", "enzo.wav")
    sound = pygame.mixer.Sound(sound_path)
    sound.set_volume(1.0)
    sound.play()


def create_border_walls(width: int, height: int, cell: int,
                        walls_group: pygame.sprite.Group[Wall]) -> None:
    for x0 in range(width + 2):
        walls_group.add(Wall(x0 * cell, 0, cell, cell))
        walls_group.add(Wall(x0 * cell, (height + 1) * cell, cell, cell))

    for y0 in range(height + 2):
        walls_group.add(Wall(0, y0 * cell, cell, cell))
        walls_group.add(Wall((width + 1) * cell, y0 * cell, cell, cell))


def create_walls(cell_walls: list[dict[str, int]], width: int, height: int,
                 cell: int, walls_group: pygame.sprite.Group[Wall],
                 color_ft: list[tuple[int, int]]) -> None:
    idx = 0
    for y0 in range(height):
        for x0 in range(width):
            cell_x = x0 * cell + cell
            cell_y = y0 * cell + cell
            if x0 % 2 != 0 and y0 % 2 != 0:
                walls_group.add(Wall(cell_x, cell_y, cell, cell))
            if x0 % 2 == 0 and y0 % 2 == 0:
                if (x0, y0) in color_ft:
                    walls_group.add(Wall(cell_x - cell, cell_y - cell, cell,
                                         cell))
                if cell_walls[idx].get("S") == 1 and y0 + 1 < height:
                    walls_group.add(Wall(cell_x, cell_y + cell, cell, cell))
                if cell_walls[idx].get("E") == 1 and x0 + 1 < width:
                    walls_group.add(Wall(cell_x + cell, cell_y, cell, cell))
                idx += 1
    create_border_walls(width, height, cell, walls_group)


def game(player: Player, arrival_group: pygame.sprite.Group[End],
         screen: pygame.Surface,
         all_sprites: pygame.sprite.AbstractGroup[Any], won: bool,
         arrival: End, walls_group: pygame.sprite.Group[Wall],
         height: int, width: int, cell: int) -> bool:
    lines = ["Play with :",
             "   [↑]   ",
             "[←][↓][→]"]
    font = pygame.font.SysFont('monospace', 23)
    for nb, line in enumerate(lines):
        surf = font.render(line, True, WHITE)
        screen.blit(surf, ((width+2)*cell+10, (height//2)*cell + nb * 35))
    player.update(walls_group)
    arrival.update() if hasattr(arrival, 'update') else None
    all_sprites.draw(screen)
    if won:
        screen.fill(BLACK)
        return True
    touch = pygame.sprite.spritecollideany(player, arrival_group)
    if touch:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sound_path = os.path.join(base_dir, "..", "resources", "scary.wav")
        sound = pygame.mixer.Sound(sound_path)
        sound.set_volume(1.0)
        sound.play()
        return True
    return False


def draw_overlay(screen: pygame.Surface, screen_size: tuple[int, int],
                 bg: pygame.Surface, cell: int) -> None:
    bg_scaled = pygame.transform.scale(bg, screen_size)
    screen.blit(bg_scaled, (0, 0))
    overlay = pygame.Surface((screen_size), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    font = pygame.font.SysFont('monospace', 23)
    write = font.render("- QUIT -", True, RED)
    screen.blit(write, (0, screen_size[1] - 40))
    font = pygame.font.SysFont('monospace', 23)
    write = font.render("- PLAY AGAIN -", True, RED)
    screen.blit(write, (0, screen_size[1] - 110))


def draw_maze(maze_datas: dict[str, Any], i: int,
              maze: MazeGenerator) -> None:
    output_file = str(maze_datas['OUTPUT_FILE'])
    with open(output_file, "r") as hexa:
        hexas = hexa.read()
    raw_inp = maze_datas.get("ENTRY")
    raw_outp = maze_datas.get("EXIT")
    raw_width = maze_datas.get("WIDTH")
    raw_height = maze_datas.get("HEIGHT")

    if not isinstance(raw_inp, tuple) or not isinstance(raw_outp, tuple):
        raise ValueError("ERROR: invalid ENTRY or EXIT")
    if not isinstance(raw_width, int) or not isinstance(raw_height, int):
        raise ValueError("ERROR: invalid WIDTH or HEIGHT")

    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    play_sound()

    inp: tuple[int, int] = raw_inp
    outp: tuple[int, int] = raw_outp
    width: int = raw_width
    height: int = raw_height

    color_ft = [(2, 2), (2, 3), (2, 4), (3, 4),
                (4, 4), (4, 5), (4, 6), (6, 2),
                (7, 2), (8, 2), (8, 3), (8, 4),
                (7, 4), (6, 4), (6, 5), (6, 6), (7, 6), (8, 6)]
    cell_walls = run_maze(hexas, width, height)

    nb_lines = 7
    line_h = 35
    menu_space = 20
    game_panel = 200
    info = pygame.display.Info()
    max_w = info.current_w - 50
    max_h = info.current_h - 100
    cell_w = max_w // (width + 2)
    menu_h = nb_lines * line_h + menu_space
    cell_h = (max_h - menu_h) // (height + 2)
    cell = min(cell_w, cell_h)
    cell = max(5, min(20, cell))
    cell = min(cell_w, cell_h)
    maze_w = (width + 2) * cell
    maze_h = (height + 2) * cell
    screen_size = (max(maze_w, 500) + game_panel, maze_h + menu_h)

    pygame.display.set_caption("A_maze_ing")
    screen = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    fps = 60

    font = pygame.font.SysFont('monospace', 23)
    lines = ["=== A_Maze_Ing ===",
             "1- Re-generate a new maze",
             "2- Show path from entry to exit",
             "3- Rotate maze colors",
             "4- Play Maze_Game",
             "5- Show the maze seed",
             "6- Quit"]
    maze_bottom = maze_h + 10
    surf0 = pygame.Rect(60, maze_bottom, 140, 20)
    surf1 = pygame.Rect(0, maze_bottom + 35, 350, 30)
    surf2 = pygame.Rect(0, maze_bottom + 35*2, 500, 30)
    surf3 = pygame.Rect(0, maze_bottom + 35*3, 300, 30)
    surf4 = pygame.Rect(0, maze_bottom + 35*4, 250, 30)
    surf5 = pygame.Rect(0, maze_bottom + 35*5, 300, 30)
    surf6 = pygame.Rect(0, maze_bottom + 35*6, 100, 30)

    COLORS = [WHITE, YELLOW, PINK, PURPLE, BROWN, GOLD, GRAY]
    surf_lst = []
    for nb, line in enumerate(lines):
        surf = font.render(line, True, COLORS[i])
        surf_lst.append(surf)

    path_coordinates = calcul_path_coordinates(inp, find_path(maze_datas))
    show_path = False

    x = 0
    y = 0
    x1, y1 = inp
    x2, y2 = outp

    player = Player(inp, width, height, cell)
    all_sprites: pygame.sprite.AbstractGroup[Any] = pygame.sprite.Group()
    all_sprites.add(player)

    arrival = End(raw_outp, cell)
    arrival_group: pygame.sprite.Group[End] = pygame.sprite.Group()
    arrival_group.add(arrival)
    all_sprites.add(arrival)
    won = False
    go_gaming = False

    walls_group: pygame.sprite.Group[Wall] = pygame.sprite.Group()
    create_border_walls(width, height, cell, walls_group)
    create_walls(cell_walls, width, height, cell, walls_group, color_ft)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(base_dir, "..", "resources", "fnaf.png")
    bg = pygame.image.load(img_path).convert()
    bg = pygame.transform.scale(bg, screen_size)

    while True:

        mouse_pos = change_mouse_cursor(surf1, surf2, surf3, surf4, surf0,
                                        surf5, surf6)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if surf0.collidepoint(mouse_pos):
                        easter_egg()

                    elif surf1.collidepoint(mouse_pos):
                        config_file = str(maze_datas['CONFIG_FILE'])
                        maze = MazeGenerator(config_file)
                        maze.create_maze()
                        pygame.quit()
                        draw_maze(maze.config, i, maze)

                    elif surf2.collidepoint(mouse_pos):
                        play_sound()
                        if show_path is False:
                            print_path(cell_walls, width, height, cell, screen,
                                       x, y, x1, y1, x2, y2, color_ft,
                                       path_coordinates, COLORS[i])
                            hide_path(surf_lst, screen, font,
                                      COLORS[i], lines, maze_bottom )
                        else:
                            rm_path(cell_walls, width, height, cell, screen,
                                       x, y, x1, y1, x2, y2, color_ft,
                                       path_coordinates, COLORS[i])
                            show_the_path(surf_lst, screen, font,
                                          COLORS[i], lines, maze_bottom)
                        show_path = not show_path

                    elif surf3.collidepoint(mouse_pos):
                        play_sound()
                        i += 1
                        if show_path is True:
                            print_path(cell_walls, width, height, cell, screen,
                                       x, y, x1, y1, x2, y2, color_ft,
                                       path_coordinates, COLORS[i])
                        else:
                            print_walls(cell_walls, width, height, cell,
                                        screen, x, y, x1, y1, x2, y2, color_ft,
                                        COLORS[i])
                        if i == 6:
                            i = -1

                    elif surf4.collidepoint(mouse_pos):
                        play_sound()
                        if show_path:
                            print("Please, hide the path!")
                        else:
                            won = False
                            go_gaming = True
                            player.kill()
                            player = Player(inp, width, height, cell)
                            arrival = End(raw_outp, cell)
                            all_sprites.empty()
                            arrival_group.empty()
                            all_sprites.add(player)
                            all_sprites.add(arrival)
                            arrival_group.add(arrival)
                            screen.fill(BLACK)
                            pygame.draw.rect(screen, COLORS[i],
                                            (x, y, (width+2) * cell, (height+2) * cell), cell)
                            print_walls(cell_walls, width, height, cell, screen, x, y, x1,
                                        y1, x2, y2, color_ft, COLORS[i])

                    elif surf5.collidepoint(mouse_pos):
                        play_sound()
                        print(maze.last_seed)

                    elif surf6.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit(0)

            else:
                pygame.draw.rect(screen, COLORS[i],
                                 (x, y, (width+2) * cell, (height+2) * cell),
                                 cell)
                print_walls(cell_walls, width, height, cell, screen, x, y, x1,
                            y1, x2, y2, color_ft, COLORS[i])
                surf_lst = []
                for nb, line in enumerate(lines):
                    surf = font.render(line, True, COLORS[i])
                    surf_lst.append(surf)
                    screen.blit(surf, (1, maze_bottom + nb * line_h))
        if go_gaming:
            won = game(player, arrival_group, screen, all_sprites, won,
                       arrival, walls_group, height, width, cell)
            if won:
                draw_overlay(screen, screen_size, bg, cell)

        pygame.display.update()
        clock.tick(fps)
