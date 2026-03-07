from __future__ import annotations
from collections import deque
from typing import Literal, Any
import random
from pydantic import BaseModel, Field, model_validator


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

        if self.seed is not None and not (0 <= self.seed <= 2**32 - 1):
            raise ValueError(f"SEED must be between 0 and {2**32 - 1},"
                             f" got '{self.seed}'")

        PATTERN_WALLS = {
            (4, 1), (2, 2), (4, 2), (6, 2), (7, 2), (8, 2),
            (2, 3), (8, 3), (1, 4), (2, 4), (3, 4), (4, 4),
            (6, 4), (7, 4), (8, 4), (4, 5), (6, 5), (1, 6),
            (2, 6), (4, 6), (6, 6), (7, 6), (8, 6),
        }

        entry_pos = (self.entry[0], self.entry[1])
        exit_pos = (self.exit[0], self.exit[1])

        if entry_pos in PATTERN_WALLS:
            raise ValueError(
                f"Entry {entry_pos} is on a '42' pattern wall"
            )
        if exit_pos in PATTERN_WALLS:
            raise ValueError(
                f"Exit {exit_pos} is on a '42' pattern wall"
            )

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
        self.config: dict[str, Any] = {}
        self.last_seed: int = 0

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
        raw_seed = self.config.get("SEED")
        config_seed = int(raw_seed) if raw_seed is not None else None
        if config_seed is None:
            seed = random.randint(0, 2**32 - 1)
        else:
            seed = config_seed
            self.config["SEED"] = None
        self.last_seed = seed
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

        if not bool(self.config["PERFECT"]):
            for x in range(1, width + 1):
                if self.maze[f"{x}:{height}"] == 1:
                    self.maze[f"{x}:{height}"] = 0
            for y in range(1, height + 1):
                if self.maze[f"{width}:{y}"] == 1:
                    self.maze[f"{width}:{y}"] = 0

        entry_x, entry_y = self.config["ENTRY"]
        exit_x, exit_y = self.config["EXIT"]
        self.maze[f'{entry_x}:{entry_y}'] = 0
        self.maze[f'{exit_x}:{exit_y}'] = 0

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
        """Fix isolated regions by connecting them to the main region.

        Uses flood-fill to find all disconnected groups of open cells
        and connects each one to the main region via BFS.
        """
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])

        def flood_fill(sx: int, sy: int, visited: set[str]) -> set[str]:
            """Return all open cells reachable from (sx, sy)."""
            region: set[str] = set()
            stack = [(sx, sy)]
            while stack:
                x, y = stack.pop()
                key = f"{x}:{y}"
                if key in visited or key in region:
                    continue
                if self.maze.get(key, 1) != 0:
                    continue
                region.add(key)
                for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                    nx, ny = x + dx, y + dy
                    if 1 <= nx <= width and 1 <= ny <= height:
                        stack.append((nx, ny))
            return region

        def connect_to_main(isolated: set[str], main: set[str]) -> None:
            """
            BFS from isolated region to find shortest path to main region.
            """
            queue: deque[tuple[int, int, list[tuple[int, int]]]] = deque()
            visited: set[str] = set(isolated)
            for key in isolated:
                x, y = map(int, key.split(":"))
                queue.append((x, y, [(x, y)]))

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
                    if nkey in main:
                        for px, py in new_path:
                            self.maze[f"{px}:{py}"] = 0
                        return
                    queue.append((nx, ny, new_path))

        # Find all regions
        visited: set[str] = set()
        regions: list[set[str]] = []
        for y in range(1, height + 1):
            for x in range(1, width + 1):
                key = f"{x}:{y}"
                if self.maze.get(key, 1) == 0 and key not in visited:
                    region = flood_fill(x, y, visited)
                    visited |= region
                    regions.append(region)

        if not regions:
            return

        # Largest region = main
        main_region = max(regions, key=len)
        isolated_groups = [r for r in regions if r is not main_region]

        for isolated in isolated_groups:
            connect_to_main(isolated, main_region)
            main_region |= isolated

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
        entry_x, entry_y = self.config["ENTRY"]
        exit_x, exit_y = self.config["EXIT"]

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
