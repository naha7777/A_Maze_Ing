from sources.draw_path import calcul_path_coordinates, find_path
from sources.maze_generator import MazeGenerator
from typing import Any
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

try:
    import pygame
except ModuleNotFoundError:
    print("ERROR: can't use pygame")
    exit(1)


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


def run_maze(hexa: str, w : int, h: int) -> dict:
    north = ["1", "3", "5", "7", "9", "B", "D", "F"]
    south = ["4", "5", "6", "7", "C", "D", "E", "F"]
    est = ["2", "3", "6", "7", "A", "B", "E", "F"]
    west = ["8", "9", "A", "B", "C", "D", "E", "F"]
    cell_walls = []
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


def print_walls(cell_walls: list, width: int, height: int, cell: int,
                screen: pygame.Surface, x: int, y: int, x1: int, y1: int,
                x2: int, y2: int, color_ft: list, color: tuple, i: int) -> None:
    # x0 = i % width
    # y0 = i // width
    # cell_x = x + x0 * cell
    # cell_y = y + y0 * cell
    # while cell_y < height:
    #     while cell_x < width:
    #         if cell_x % 2 != 0 and cell_y % 2 != 0:
    #             pygame.draw.rect(screen,
    #                             GREEN,
    #                             (cell_x, cell_y, cell, cell))

    for i, dic in enumerate(cell_walls):
            x0 = i % width
            y0 = i // width
            cell_x = x + x0 * cell
            cell_y = y + y0 * cell
            cellx_i = x + x1 * cell
            celly_i = y + y1 * cell
            if cell_x == cellx_i and cell_y == celly_i:
                pygame.draw.rect(screen,
                                 GREEN,
                                 (cellx_i, celly_i, cell, cell))
            cellx_o = x + x2 * cell
            celly_o = y + y2 * cell
            if cell_x == cellx_o and cell_y == celly_o:
                pygame.draw.rect(screen,
                                 RED,
                                 (cellx_o, celly_o, cell, cell))
            if dic.get("W") == 1:
                pygame.draw.rect(screen,
                                 color,
                                 (cell_x, cell_y+20, cell, cell))
            if dic.get("E") == 1:
                pygame.draw.rect(screen,
                                 color,
                                 (cell_x+40, cell_y+20, cell, cell))
            for coordinate in color_ft:
                xc, yc = coordinate
                cell_xft = x + xc * cell
                cell_yft = y + yc * cell
                if cell_x == cell_xft and cell_y == cell_yft:
                    pygame.draw.rect(screen,
                                     BLUE,
                                     (cell_x, cell_y, cell, cell))


def print_path(cell_walls: list, width: int, cell: int, screen: pygame.Surface,
               x: int, y: int, x1: int, y1: int, x2: int, y2: int,
               color_ft: list, path_coordinates: list, color: tuple) -> None:
    print_walls(cell_walls, width, cell, screen, x, y, x1, y1, x2, y2,
                color_ft, color)
    for i, dic in enumerate(cell_walls):
        x0 = i % width
        y0 = i // width
        cell_x = x + x0 * cell
        cell_y = y + y0 * cell
        for coordinate in path_coordinates:
            xc, yc = coordinate
            cell_xft = x + xc * cell
            cell_yft = y + yc * cell
            if cell_x == cell_xft and cell_y == cell_yft:
                pygame.draw.rect(screen,
                                GREEN,
                                (cell_x, cell_y, cell, cell))


def change_mouse_cursor(surf1: pygame.rect.Rect, surf2: pygame.rect.Rect,
                        surf3: pygame.rect.Rect, surf4: pygame.rect.Rect,
                        surf5: pygame.rect.Rect) -> tuple:
    mouse_pos = pygame.mouse.get_pos()
    if surf1.collidepoint(mouse_pos) or surf2.collidepoint(mouse_pos)\
    or surf3.collidepoint(mouse_pos) or surf4.collidepoint(mouse_pos)\
    or surf5.collidepoint(mouse_pos):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
    else:
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    return mouse_pos


def hide_path(surf_lst: list, height: int, cell: int, screen: pygame.Surface,
              font: pygame.font.Font, COLORS: list, i: int,
              lines: list) -> None:
    rect_txt = surf_lst[2].get_rect(topleft=(0, (height+3)*cell + 35*2))
    pygame.draw.rect(screen, (0, 0, 0), rect_txt)
    font.render("Hide path", True, COLORS[i])
    lines[2] = "2- Hide path"


def show_the_path(surf_lst: list, height: int, cell: int,
                  screen: pygame.Surface, font: pygame.font.Font,
                  COLORS: list, i: int, lines: list) -> None:
    rect_txt = surf_lst[2].get_rect(topleft=(0, (height+3)*cell + 35*2))
    pygame.draw.rect(screen, (0, 0, 0), rect_txt)
    lines[2] = "2- Show path from entry to exit"
    font.render(lines[2], True, COLORS[i])


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


def draw_maze(maze_datas: dict, i: int) -> None:
    with open(maze_datas['OUTPUT_FILE'], "r") as hexa:
        hexas = hexa.read()
    inp = maze_datas.get("ENTRY")
    outp = maze_datas.get("EXIT")
    width = maze_datas.get("WIDTH")
    height = maze_datas.get("HEIGHT")

    color_ft = [(2, 2), (2, 3), (2, 4), (3, 4),
                (4, 4), (4, 5), (4, 6), (6, 2),
                (7, 2), (8, 2), (8, 3), (8, 4),
                (7, 4), (6, 4), (6, 5), (6, 6), (7, 6), (8, 6)]
    cell_walls = run_maze(hexas, width, height)
    cell = 20

    pygame.init()
    pygame.font.init()
    pygame.mixer.init()
    pygame.display.set_caption("A_maze_ing")
    screen = pygame.display.set_mode((width*50, height*50))
    clock = pygame.time.Clock()
    fps = 60

    font = pygame.font.SysFont('monospace', 23)
    lines = ["=== A_Maze_Ing ===",
             "1- Re-generate a new maze",
             "2- Show path from entry to exit",
             "3- Rotate maze colors",
             "4- Quit"]
    surf1 = pygame.Rect(0, (height+3)*cell + 32, 350, 30)
    surf2 = pygame.Rect(0, (height+3)*cell + 32*2, 500, 30)
    surf3 = pygame.Rect(0, (height+3)*cell + 32*3, 300, 30)
    surf4 = pygame.Rect(0, (height+3)*cell + 32*4, 100, 30)
    surf5 = pygame.Rect(60, (height+3)*cell, 140, 20)

    COLORS = [WHITE, YELLOW, PINK, PURPLE, BROWN, GOLD, GRAY]

    path_coordinates = calcul_path_coordinates(inp, find_path(maze_datas))
    show_path = False

    x = 0
    y = 0
    x1, y1 = inp
    x2, y2 = outp

    while True:

        mouse_pos = change_mouse_cursor(surf1, surf2, surf3, surf4, surf5)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:

                    if surf1.collidepoint(mouse_pos):
                        play_sound()
                        config_file = maze_datas['CONFIG_FILE']
                        maze = MazeGenerator(config_file)
                        maze.create_maze()
                        pygame.quit()
                        draw_maze(maze.config, i)

                    elif surf2.collidepoint(mouse_pos):
                        play_sound()
                        if show_path is False:
                            print_path(cell_walls, width, cell, screen, x, y,
                                       x1, y1, x2, y2, color_ft,
                                       path_coordinates, COLORS[i])
                            hide_path(surf_lst, height, cell, screen, font,
                                      COLORS, i, lines)
                        else:
                            print_walls(cell_walls, width, cell, screen, x, y,
                                        x1, y1, x2, y2, color_ft, COLORS[i])
                            show_the_path(surf_lst, height, cell, screen, font,
                                          COLORS, i, lines)
                        show_path = not show_path

                    elif surf3.collidepoint(mouse_pos):
                        play_sound()
                        i += 1
                        if show_path is False:
                            print_path(cell_walls, width, cell, screen, x, y,
                                       x1, y1, x2, y2, color_ft,
                                       path_coordinates, COLORS[i])
                        else:
                            print_walls(cell_walls, width, cell, screen, x, y,
                                        x1, y1, x2, y2, color_ft, COLORS[i])
                        if i == 6:
                            i = -1

                    elif surf4.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

                    elif surf5.collidepoint(mouse_pos):
                        easter_egg()

            else:
                pygame.draw.rect(screen,
                                COLORS[i],
                                (x, y, (width+2) * cell, (height+2) * cell),
                                 cell)
                print_walls(cell_walls, width, height, cell, screen, x, y, x1,
                            y1, x2, y2, color_ft, COLORS[i], i)
                surf_lst = []
                for nb, line in enumerate(lines):
                    surf = font.render(line, True, COLORS[i])
                    surf_lst.append(surf)
                    screen.blit(surf, (1, (height+3)*cell + nb * 35))

        pygame.display.update()
        clock.tick(fps)


if __name__ == "__main__":
    draw_maze()
