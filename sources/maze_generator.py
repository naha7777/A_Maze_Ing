from __future__ import annotations
from collections import deque
from typing import Literal, Any
import random
from pydantic import BaseModel, Field, model_validator


PATTERN_WALLS: set[tuple[int, int]] = {
    (4, 1), (2, 2), (4, 2), (6, 2), (7, 2), (8, 2),
    (2, 3), (8, 3), (1, 4), (2, 4), (3, 4), (4, 4),
    (6, 4), (7, 4), (8, 4), (4, 5), (6, 5), (1, 6),
    (2, 6), (4, 6), (6, 6), (7, 6), (8, 6),
}


class MazeConfig(BaseModel):
    """Validated configuration for the maze generator."""
    width: int = Field(..., ge=4, le=250)
    height: int = Field(..., ge=4, le=250)
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
            raise ValueError("Output file must end with .txt")

        if not (0 <= self.entry[0] <= self.width
                and 0 <= self.entry[1] <= self.height):
            raise ValueError(f"Entry {self.entry} out of bounds")

        if not (0 <= self.exit[0] <= self.width
                and 0 <= self.exit[1] <= self.height):
            raise ValueError(f"Exit {self.exit} out of bounds")

        if self.entry[0] == self.exit[0] and self.entry[1] == self.exit[1]:
            raise ValueError("Exit and Entry are in the same cell")

        dx = abs(self.entry[0] - self.exit[0])
        dy = abs(self.entry[1] - self.exit[1])
        if (dx == 2 and dy == 0) or (dx == 0 and dy == 2):
            raise ValueError("Exit and Entry are too close"
                             "(directly adjacent cells)")

        if self.seed is not None and not (0 <= self.seed <= 2**32 - 1):
            raise ValueError(f"SEED must be between 0 and {2**32 - 1}, "
                             f"got '{self.seed}'")

        entry_pos = (self.entry[0], self.entry[1])
        exit_pos = (self.exit[0], self.exit[1])
        if entry_pos in PATTERN_WALLS:
            raise ValueError(f"Entry {entry_pos} is on a '42' pattern wall")
        if exit_pos in PATTERN_WALLS:
            raise ValueError(f"Exit {exit_pos} is on a '42' pattern wall")

        if self.width >= 233 and self.print_mode == "pygame":
            raise ValueError("Width too hight for pygame mode")

        if self.height >= 88 and self.print_mode == "pygame":
            raise ValueError("Height too hight for pygame mode")

        return self


def parse_coords(value: str, key: str) -> list[int]:
    """Parse a coordinate string 'x,y' into a list of two integers."""
    parts = value.strip().split(",")
    if len(parts) != 2:
        raise ValueError(f"{key} must have exactly 2 values "
                         f"separated by a comma, got '{value}'")
    result: list[int] = []
    for part in parts:
        part = part.strip()
        if not part.lstrip("-").isdigit():
            raise ValueError(f"{key} values must be integers, got '{part}' in"
                             f" '{value}'")
        result.append(int(part))
    return result


def parse_perfect(value: str) -> bool:
    """Parse a boolean string for the PERFECT config key."""
    normalised = value.strip().upper()
    if normalised not in ("TRUE", "FALSE"):
        raise ValueError(f"PERFECT must be True or False "
                         f", got '{value}'")
    return normalised == "TRUE"


class MazeGenerator:
    """Generate a maze from a configuration file."""

    def __init__(self, config_file: str) -> None:
        self.maze: dict[str, int] = {}
        self.config: dict[str, Any] = {}
        self.last_seed: int = 0

        mandatory_keys = ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                          "OUTPUT_FILE", "PERFECT"]
        additional_keys = ["SEED", "PRINT_MODE"]

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
            raise ValueError(f"WIDTH must be an integer, got '{raw_width}'")
        try:
            height = int(raw_height)
        except ValueError:
            raise ValueError(f"HEIGHT must be an integer, got '{raw_height}'")

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
        self.config["ENTRY"] = (validated.entry[0] * 2,
                                validated.entry[1] * 2)
        self.config["EXIT"] = (validated.exit[0] * 2,
                               validated.exit[1] * 2)
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
        """
        Generate the maze using a recursive backtracker (DFS) algorithm.

        The '42' pattern is stamped onto the grid BEFORE the DFS starts so
        the algorithm naturally carves around it:
        - Pattern wall cells (value=1) are never carved through by DFS.
        - Pattern open cells (value=0) are pre-marked as visited so DFS
          connects to them without re-walling them.
        """
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

        use_42 = width >= 11 and height >= 9
        if use_42:
            for (wx, wy) in PATTERN_WALLS:
                self.maze[f"{wx}:{wy}"] = 1

        pre_visited: set[str] = set()

        all_cells = [
            (x, y)
            for x in range(1, width, 2)
            for y in range(1, height, 2)
            if f"{x}:{y}" not in pre_visited
        ]
        start_x, start_y = random.choice(all_cells)
        self.maze[f"{start_x}:{start_y}"] = 0

        directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
        stack: list[tuple[int, int]] = [(start_x, start_y)]

        while stack:
            x, y = stack[-1]
            neighbors: list[tuple[int, int, int, int]] = []
            for dx, dy in directions:
                nx = x + dx
                ny = y + dy
                if not (1 <= nx <= width+1 and 1 <= ny <= height+1):
                    continue
                nkey = f"{nx}:{ny}"
                if self.maze[nkey] == 0 or nkey in pre_visited:
                    continue
                wall_x = x + dx // 2
                wall_y = y + dy // 2
                if use_42 and (wall_x, wall_y) in PATTERN_WALLS:
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
            walls = [
                (x, y)
                for x in range(1, width + 1)
                for y in range(1, height + 1)
                if self.maze[f"{x}:{y}"] == 1
                and (x % 2 == 1 or y % 2 == 1)
                and (not use_42 or (x, y) not in PATTERN_WALLS)
            ]
            extra = max(1, len(walls) // 20)
            for x, y in random.sample(walls, min(extra, len(walls))):
                self.maze[f"{x}:{y}"] = 0

        entry_x, entry_y = self.config["ENTRY"]
        exit_x, exit_y = self.config["EXIT"]

        self.maze[f"{entry_x+1}:{entry_y+1}"] = 0
        self.maze[f"{exit_x+1}:{exit_y+1}"] = 0

    def fix_isolated(self) -> None:
        """Fix isolated regions by connecting them to the main region."""
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])

        def flood_fill(sx: int, sy: int, visited: set[str]) -> set[str]:
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

        main_region = max(regions, key=len)
        isolated_groups = [r for r in regions if r is not main_region]
        for isolated in isolated_groups:
            connect_to_main(isolated, main_region)
            main_region |= isolated

    def encode_hex(self, x: int, y: int) -> str:
        """Encode the walls of a cell as a single hexadecimal character."""
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

    def solve(self) -> list[str]:
        """
        BFS shortest path from entry to exit, returns cardinal directions.
        """
        from collections import deque
        entry_x, entry_y = self.config["ENTRY"]
        exit_x, exit_y = self.config["EXIT"]

        entry_x += 1
        entry_y += 1
        exit_x += 1
        exit_y += 1
        goal = (exit_x, exit_y)

        queue: deque[tuple[tuple[int, int], list[str]]] = deque()
        queue.append(((entry_x, entry_y), []))
        visited: set[tuple[int, int]] = {(entry_x, entry_y)}

        while queue:
            (x, y), directions = queue.popleft()
            if (x, y) == goal:
                return directions
            for dx, dy, direction in ((0, -1, "N"),
                                      (0, 1, "S"),
                                      (1, 0, "E"),
                                      (-1, 0, "W")):
                nx, ny = x + dx, y + dy
                if (nx, ny) in visited:
                    continue
                if self.maze[f"{nx}:{ny}"] == 1:
                    continue
                visited.add((nx, ny))
                queue.append(((nx, ny), directions + [direction]))
        return []

    def write_output(self) -> None:
        """Write the maze to the output file in hexadecimal format."""
        width = int(self.config["WIDTH"])
        height = int(self.config["HEIGHT"])
        output_file = str(self.config["OUTPUT_FILE"])
        entry_x, entry_y = self.config["ENTRY"]
        exit_x, exit_y = self.config["EXIT"]
        solve = self.solve()

        with open(output_file, "w") as f:
            for y in range(1, height + 1, 2):
                row = [self.encode_hex(x, y) for x in range(1, width + 1, 2)]
                f.write("".join(row) + "\n")
            f.write(f"\n{entry_x},{entry_y}\n")
            f.write(f"{exit_x},{exit_y}\n")
            f.write("".join(solve) + "\n")

    def create_maze(self) -> None:
        """Run the full maze creation pipeline."""
        self.init_grid()
        self.generate()
        self.fix_isolated()
        self.write_output()
