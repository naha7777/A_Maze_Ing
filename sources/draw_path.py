from sources.draw_ascii import run_maze, color_text, rgb
from typing import Any


def find_path(maze_datas: dict[str, Any]) -> str:
    with open(maze_datas['OUTPUT_FILE'], "r") as file:
        text = file.read()

    lines = text.split("\n")
    lines.reverse()

    path = lines[1]
    return path


def calcul_path_coordinates(input: tuple[int, int],
                            path: str) -> list[tuple[int, int]]:
    path_coordinates = []

    for c in path:
        if c not in "NSEW":
            continue
        x1, y1 = input

        if c == "S":
            input = (x1, y1+1)
        elif c == "E":
            input = (x1+1, y1)
        elif c == "N":
            input = (x1, y1-1)
        elif c == "W":
            input = (x1-1, y1)

        path_coordinates.append(input)
    return path_coordinates


def draw_path(maze_datas: dict[str, Any], color: str) -> None:
    with open(maze_datas['OUTPUT_FILE'], "r") as hexa:
        hexas = hexa.read()

    inp: tuple[int, int] = maze_datas["ENTRY"]
    outp: tuple[int, int] = maze_datas["EXIT"]
    width: int = maze_datas["WIDTH"]
    height: int = maze_datas["HEIGHT"]
    x = 0

    cell_walls = run_maze(hexas, width, height)
    wall = "\u2588"

    color_name = color.split(".")[1]
    color_rgb = getattr(rgb, color_name)

    color_ft = [(2, 2), (2, 3), (2, 4), (3, 4),
                (4, 4), (4, 5), (4, 6), (6, 2),
                (7, 2), (8, 2), (8, 3), (8, 4),
                (7, 4), (6, 4), (6, 5), (6, 6), (7, 6), (8, 6)]

    grid = [[" " for _ in range(width)] for _ in range(height)]

    path = find_path(maze_datas)
    inp_grid = (inp[0] - 1, inp[1] - 1)
    outp_grid = (outp[0] - 1, outp[1] - 1)
    path_coordinates = calcul_path_coordinates(inp_grid, path)

    i = 0
    for y in range(height):
        for x in range(width):
            if (x, y) in color_ft:
                grid[y-1][x-1] = (color_text(wall, rgb.BLUE))
            if (x, y) == inp_grid:
                grid[y][x] = (color_text(wall, rgb.GREEN))
            if (x, y) == outp_grid:
                grid[y][x] = (color_text(wall, rgb.RED))
            if x % 2 != 0 and y % 2 != 0:
                grid[y][x] = (color_text(wall, color_rgb))
            if (x, y) in path_coordinates:
                if (x, y) == path_coordinates[len(path_coordinates)-1]:
                    continue
                else:
                    grid[y][x] = (color_text(wall, rgb.GREEN))
            if x % 2 == 0 and y % 2 == 0:
                if cell_walls[i].get("S") == 1 and y + 1 < height:
                    grid[y + 1][x] = color_text(wall, color_rgb)
                if cell_walls[i].get("E") == 1 and x + 1 < width:
                    grid[y][x + 1] = color_text(wall, color_rgb)
                i += 1

    for x in range(width+2):
        if x == width+1:
            print(color_text(wall, color_rgb))
        else:
            print(color_text(wall, color_rgb), end="")

    for col in grid:
        print(color_text(wall, color_rgb), end="")
        for cell in col:
            print(cell, end="")
        print(color_text(wall, color_rgb))

    for x in range(width+2):
        if x == width+1:
            print(color_text(wall, color_rgb))
        else:
            print(color_text(wall, color_rgb), end="")
