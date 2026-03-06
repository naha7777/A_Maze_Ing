from sources.maze_generator import MazeGenerator
from sources.draw_ascii import draw_ascii
from sources.draw_path import draw_path

def interactions(maze: MazeGenerator):
    show_path = False
    i = 0
    color_list = ["rgb.WHITE", "rgb.YELLOW",
                  "rgb.PINK", "rgb.PURPLE",
                  "rgb.BROWN", "rgb.GOLD", "rgb.GRAY",]
    while True:
        print("\n=== A-maze-ing ===")
        path = "Hide path" if show_path else "Show path from entry to exit"
        print("1- Re-generate a new maze")
        print(f"2- {path}")
        print("3- Rotate maze colors")
        print("4- Quit")

        choice = input("Choice (1-4): ")

        try:

            if int(choice) == 1:
                maze.create_maze()
                draw_ascii(maze.config, color_list[i])

            elif int(choice) == 2:
                if show_path is False:
                    draw_path(maze.config, color_list[i])
                else:
                    draw_ascii(maze.config, color_list[i])
                show_path = not show_path

            elif int(choice) == 3:
                i += 1
                if show_path is True:
                    draw_path(maze.config, color_list[i])
                else:
                    draw_ascii(maze.config, color_list[i])
                if i == 6:
                    i = -1

            elif int(choice) == 4:
                exit(0)

            else:
                print("ERROR: please put 1, 2, 3 or 4 !")
                exit(1)

        except ValueError as e:
            print(e)
            exit(1)


if __name__ == "__main__":
    interactions()
