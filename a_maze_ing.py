from sources.draw_ascii import draw_ascii
from sources.draw_maze import draw_maze
from sources.ascii_interactions import interactions
from sources.maze_generator import MazeGenerator
import pydantic
import sys


def a_maze_ing() -> None:

    try:
        if len(sys.argv) != 2:
            raise ValueError("must have 2 arg")
        maze = MazeGenerator(sys.argv[1])
        maze.create_maze()

        if maze.config["PRINT_MODE"] == "pygame":
            draw_maze(maze.config, 0, maze)

        else:
            draw_ascii(maze.config, "rgb.WHITE")
            interactions(maze)

    except pydantic.ValidationError as e:
        for error in e.errors():
            print(f"ERROR: {error['msg'].replace('Value error, ', '')}")

    except KeyError as e:
        print(f"ERROR: {e}")

    except KeyboardInterrupt:
        print("\nKO")
        exit(1)


if __name__ == "__main__":
    a_maze_ing()
