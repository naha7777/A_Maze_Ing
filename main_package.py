from mazegen_anacharp_emarette import MazeGenerator, draw_maze, draw_ascii, interactions
import sys
import pydantic

def a_maze_ing() -> None:
    """Entry point: parse arguments, generate and display the maze."""
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

    except (KeyError, ValueError) as e:
        print(f"ERROR: {e}")

    except KeyboardInterrupt:
        print("\nThe program was Kill")
        exit(1)


if __name__ == "__main__":
    a_maze_ing()