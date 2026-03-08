from typing import Any


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


def color_text(text: str, rgb: tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{text}\033[0m"


class rgb():
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
    BLACK = (30, 30, 30)


def draw_ascii(maze_datas: dict[str, Any], color: str) -> None:
    with open(maze_datas['OUTPUT_FILE'], "r") as hexa:
        hexas = hexa.read()

    inp = maze_datas["ENTRY"]
    outp = maze_datas["EXIT"]
    width = maze_datas["WIDTH"]
    height = maze_datas["HEIGHT"]

    cell_walls = run_maze(hexas, width, height)
    wall = "\u2588"

    color_name = color.split(".")[1]
    color_rgb: tuple[int, int, int] = getattr(rgb, color_name)

    color_ft = [(2, 2), (2, 3), (2, 4), (3, 4),
                (4, 4), (4, 5), (4, 6), (6, 2),
                (7, 2), (8, 2), (8, 3), (8, 4),
                (7, 4), (6, 4), (6, 5), (6, 6), (7, 6), (8, 6)]

    grid = [[" " for _ in range(width)] for _ in range(height)]

    inp_grid = (inp[0] - 1, inp[1] - 1)
    outp_grid = (outp[0] - 1, outp[1] - 1)
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
