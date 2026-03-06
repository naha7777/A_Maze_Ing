from __future__ import annotations
from collections import deque
from typing import Literal
import random
from pydantic import BaseModel, Field, model_validator
import os


class MazeConfig(BaseModel):
    """Validated configuration for the maze generator."""

    width: int = Field(..., ge=4)
    height: int = Field(..., ge=4)
    entry: list[int] = Field(..., min_length=2, max_length=2)
    exit: list[int] = Field(..., min_length=2, max_length=2)
    output_file: str = Field(...)
    perfect: bool = Field(...)
    seed: int | None = Field(default=None)
    print_mode: Literal["ascii", "pygame"] = Field(default="ascii")

    @model_validator(mode="after")
    def validate_rules(self) -> MazeConfig:
        """Validate inter-field constraints."""
        if not self.output_file.endswith(".txt"):
            raise ValueError("output file must end with .txt")

        if not (
            0 < self.entry[0] < self.width * 2 + 1
            and 0 < self.entry[1] < self.height * 2 + 1
        ):
            raise ValueError("Entry can't be in this place")

        if not (
            0 < self.exit[0] < self.width * 2 + 1
            and 0 < self.exit[1] < self.height * 2 + 1
        ):
            raise ValueError("Exit can't be in this place")

        if self.entry[0] == self.exit[0] and self.entry[1] == self.exit[1]:
            raise ValueError("Exit and Entry are in the same cell")

        if (
            self.entry[0] == self.exit[0] + 1
            and self.entry[1] == self.exit[1]
            or self.entry[0] == self.exit[0] - 1
            and self.entry[1] == self.exit[1]
            or self.entry[0] == self.exit[0]
            and self.entry[1] == self.exit[1] + 1
            or self.entry[0] == self.exit[0]
            and self.entry[1] == self.exit[1] - 1
        ):
            raise ValueError("Exit and Entry are too close")

        return self


def parse_coords(value: str, key: str) -> list[int]:
    """Parse a coordinate string 'x,y' into a list of two integers.

    Args:
        value: The raw string from the config file.
        key: The config key name, used in error messages.

    Returns:
        A list of two integers [x, y].

    Raises:
        ValueError: If the format is invalid or values are not integers.
    """
    parts = value.strip().split(",")
    if len(parts) != 2:
        raise ValueError(
            f"{key} must have exactly 2 values separated by a comma,"
            f" got '{value}'"
        )
    result: list[int] = []
    for part in parts:
        part = part.strip()
        if not part.lstrip("-").isdigit():
            raise ValueError(
                f"{key} values must be integers, got '{part}' in '{value}'"
            )
        result.append(int(part))
    return result


def parse_perfect(value: str) -> bool:
    """Parse a boolean string for the PERFECT config key.

    Args:
        value: The raw string from the config file.

    Returns:
        True if the value represents true, False otherwise.

    Raises:
        ValueError: If the value is not a recognised boolean string.
    """
    normalised = value.strip().upper()
    if normalised not in ("TRUE", "FALSE"):
        raise ValueError(
            f"PERFECT must be True or False (case-insensitive),"
            f" got '{value}'"
        )
    return normalised == "TRUE"


class MazeGenerator:
    """Generate a maze from a configuration file."""

    def __init__(self, config_file: str) -> None:
        """Initialise the MazeGenerator from a configuration file.

        Args:
            config_file: Path to the .txt configuration file.

        Raises:
            KeyError: If a key is invalid or a mandatory key is missing.
            ValueError: If any value fails validation.
        """
        self.maze: dict[str, int] = {}
        self.config: dict[str, object] = {}

        mandatory_keys = [
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
        ]
        additional_keys = [
            "SEED",
            "PRINT_MODE",
        ]

        with open(config_file, "r") as f:
            config_file_content = f.read().split("\n")

        for line in config_file_content:
            if line.startswith("#"):
                continue
            if not line.strip():
                continue

            param = line.split("=", 1)
            if len(param) != 2:
                raise KeyError(f"line must be 'KEY=VALUE', got '{line}'")

            key, value = param[0].strip(), param[1].strip()

            if key not in mandatory_keys and key not in additional_keys:
                raise KeyError(f"invalid key '{key}'")

            self.config[key] = value

        missing = [k for k in mandatory_keys if k not in self.config]
        if missing:
            raise KeyError(f"missing mandatory key(s): {', '.join(missing)}")

        raw_width = str(self.config["WIDTH"])
        raw_height = str(self.config["HEIGHT"])

        try:
            width = int(raw_width)
        except ValueError:
            raise ValueError(
                f"WIDTH must be an integer, got '{raw_width}'"
            )

        try:
            height = int(raw_height)
        except ValueError:
            raise ValueError(
                f"HEIGHT must be an integer, got '{raw_height}'"
            )

        entry = parse_coords(str(self.config["ENTRY"]), "ENTRY")
        exit_ = parse_coords(str(self.config["EXIT"]), "EXIT")
        perfect = parse_perfect(str(self.config["PERFECT"]))

        seed: int | None = None
        if "SEED" in self.config:
            try:
                seed = int(str(self.config["SEED"]))
            except ValueError:
                raise ValueError(
                    f"SEED must be an integer, got '{self.config['SEED']}'"
                )

        print_mode: Literal["ascii", "pygame"] = "ascii"
        if "PRINT_MODE" in self.config:
            raw_mode = str(self.config["PRINT_MODE"])
            if raw_mode not in ("ascii", "pygame"):
                raise ValueError(
                    f"PRINT_MODE must be 'ascii' or 'pygame', got '{raw_mode}'"
                )
            print_mode = raw_mode  # type: ignore[assignment]

        validated = MazeConfig(
            width=width,
            height=height,
            entry=entry,
            exit=exit_,
            output_file=str(self.config["OUTPUT_FILE"]),
            perfect=perfect,
            seed=seed,
            print_mode=print_mode,
        )

        self.config["WIDTH"] = validated.width * 2 + 1
        self.config["HEIGHT"] = validated.height * 2 + 1
        self.config["ENTRY"] = tuple(validated.entry)
        self.config["EXIT"] = tuple(validated.exit)
        self.config["PERFECT"] = validated.perfect
        self.config["SEED"] = validated.seed
        self.config["PRINT_MODE"] = validated.print_mode
        self.config["OUTPUT_FILE"] = validated.output_file
        self.config["CONFIG_FILE"] = config_file

    def init_grid(self) -> None:
        """Initialise the maze grid with all walls set (value 1)."""
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])
        for x in range(0, width + 2):
            for y in range(0, height + 2):
                self.maze[f"{x}:{y}"] = 1

    def generate(self) -> None:
        """Generate the maze using a recursive backtracker (DFS) algorithm."""
        seed = self.config.get("SEED")
        if seed is not None:
            random.seed(seed)

        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])

        stack: list[tuple[int, int]] = []

        start_x = random.randrange(1, width, 2)
        start_y = random.randrange(1, height, 2)

        stack.append((start_x, start_y))
        self.maze[f"{start_x}:{start_y}"] = 0

        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]

        while stack:
            x, y = stack[-1]
            neighbors: list[tuple[int, int, int, int]] = []

            for dx, dy in directions:
                nx = x + dx
                ny = y + dy

                if not (1 <= nx <= width and 1 <= ny <= height):
                    continue
                if self.maze[f"{nx}:{ny}"] == 0:
                    continue

                neighbors.append((nx, ny, dx, dy))

            if neighbors:
                nx, ny, dx, dy = random.choice(neighbors)
                wall_x = x + dx // 2
                wall_y = y + dy // 2
                self.maze[f"{wall_x}:{wall_y}"] = 0
                self.maze[f"{nx}:{ny}"] = 0
                stack.append((nx, ny))
            else:
                stack.pop()

        for x in range(1, width + 1):
            if self.maze[f"{x}:{height}"] == 1:
                self.maze[f"{x}:{height}"] = 0

        for y in range(1, height + 1):
            if self.maze[f"{width}:{y}"] == 1:
                self.maze[f"{width}:{y}"] = 0

    def add_42(self) -> None:
        """Carve the '42' pattern into the maze as fully closed cells.

        The pattern is defined as a 2D grid where 1 = wall and 0 = open.
        It is placed starting at position (1, 1) in the maze.
        """
        pattern = [
            # x: 1  2  3  4  5  6  7  8  9
            [0, 0, 0, 1, 0, 0, 0, 0, 0],  # y=1
            [0, 1, 0, 1, 0, 1, 1, 1, 0],  # y=2
            [0, 1, 0, 0, 0, 0, 0, 1, 0],  # y=3
            [1, 1, 1, 1, 0, 1, 1, 1, 0],  # y=4
            [0, 0, 0, 1, 0, 1, 0, 0, 0],  # y=5
            [1, 1, 0, 1, 0, 1, 1, 1, 0],  # y=6
        ]

        for y, row in enumerate(pattern, start=1):
            for x, value in enumerate(row, start=1):
                self.maze[f"{x}:{y}"] = value

    def fix_isolated(self) -> None:
        """Fix isolated cells by opening a passage to the nearest
            open neighbour.

        An isolated cell is an open cell (value 0) surrounded by walls on
        all cardinal directions (N, S, W, E). For each such cell, the closest
        open cell is found via BFS and the wall between them is opened.
        """
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])

        def is_isolated(x: int, y: int) -> bool:
            """Return True if the cell at (x, y) is open but fully walled in.
            """
            if self.maze.get(f"{x}:{y}", 1) != 0:
                return False
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = x + dx, y + dy
                if self.maze.get(f"{nx}:{ny}", 1) == 0:
                    return False
            return True

        def open_path_to_main(sx: int, sy: int) -> None:
            """BFS from (sx, sy) to find nearest open cell and open the wall.
            """
            queue: deque[tuple[int, int, list[tuple[int, int]]]] = deque()
            visited: set[str] = {f"{sx}:{sy}"}
            queue.append((sx, sy, [(sx, sy)]))

            while queue:
                x, y, path = queue.popleft()

                for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    nx, ny = x + dx, y + dy
                    if not (1 <= nx <= width and 1 <= ny <= height):
                        continue
                    nkey = f"{nx}:{ny}"
                    if nkey in visited:
                        continue
                    visited.add(nkey)
                    new_path = path + [(nx, ny)]

                    if self.maze.get(nkey, 1) == 0:
                        for px, py in new_path:
                            self.maze[f"{px}:{py}"] = 0
                        return

                    queue.append((nx, ny, new_path))

        for y in range(1, height + 1):
            for x in range(1, width + 1):
                if is_isolated(x, y):
                    open_path_to_main(x, y)

    def encode_hex(self, x: int, y: int) -> str:
        """Encode the walls of a cell as a single hexadecimal character.

        Args:
            x: The x coordinate of the cell.
            y: The y coordinate of the cell.

        Returns:
            A single uppercase hex character representing the cell's walls.
        """
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])
        value = 0

        if y == 1 or self.maze[f"{x}:{y - 1}"] == 1:
            value |= 1 << 0

        if x == width or self.maze[f"{x + 1}:{y}"] == 1:
            value |= 1 << 1

        if y == height or self.maze[f"{x}:{y + 1}"] == 1:
            value |= 1 << 2

        if x == 1 or self.maze[f"{x - 1}:{y}"] == 1:
            value |= 1 << 3

        return hex(value)[2:].upper()

    def write_output(self) -> None:
        """Write the maze to the output file in hexadecimal format."""
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])
        output_file = str(self.config["OUTPUT_FILE"])
        entry_x, entry_y = self.config["ENTRY"]  # type: ignore[misc]
        exit_x, exit_y = self.config["EXIT"]  # type: ignore[misc]

        with open(output_file, "w") as f:
            for y in range(1, height + 1, 2):
                row = [self.encode_hex(x, y) for x in range(1, width + 1, 2)]
                f.write("".join(row) + "\n")
            f.write(f"\n{entry_x},{entry_y}\n")
            f.write(f"{exit_x},{exit_y}\n")

    def create_maze(self) -> None:
        """Run the full maze creation pipeline."""
        self.init_grid()
        self.generate()
        self.add_42()
        self.fix_isolated()
        self.write_output()
