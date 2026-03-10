_This project has been created as part of the 42 curriculum by anacharp, emarette._

# A_Maze_Ing

## Description
A_Maze_Ing is a Python program dedicated to generating and visualizing mazes.\
Its main objective is to create a tool capable of transforming a text-based configuration file into a structured maze, while providing a visual interface for the user.\
The project is divided into three main functionalities :
- Maze Generation : the program generates mazes of varying sizes. It can create "perfect mazes" (with a single path between the entrance and exit) and "unperfect mazes". The maze is generated from the data in the configuration file.
- Interactive Visualization : The program provides an interactive text-based display. The user can regenerate a maze, change the colors, and show or hide the shortest path to solve the puzzle. The user can also display the seed used for generation and reuse it in the config file to reproduce the same maze.
- Data Export : The result is saved to a text file. Each cell is represented by a hexadecimal number encoding the position of the walls (North, South, East, West).

Finally, the generation engine is designed as a reusable Python module, allowing this logic to be easily integrated into other projects.

## Instructions
Let's start with environment and package installation :
```bash
make install
```
After that, you only have to run the program with :
```bash
make run
```
It will go on the environment and execute the program with `python3 a_maze_ing.py config.txt`

Or you can do it yourself :
```bash
source .venv/bin/activate
```
And
```bash
python3 a_maze_ing.py config.txt
```

## Structure and format of our config file
The maze will be entirely generated from the data sent in the configuration file.\
All fields are required unless marked otherwise.\
The required data is as follows:
| keys |description | example |
|------|------------|---------|
|WIDTH |the width of the maze|WIDTH=15|
|HEIGHT|the height of the maze|HEIGHT=15|
|ENTRY|entry coordinates (x,y)|ENTRY=0,0|
|EXIT|exit coordinates (x,y)|EXIT=4,4|
|OUTPUT_FILE|Output file name|OUTPUT_FILE=maze.txt|
|PERFECT|Is the maze perfect or not?|PERFECT=True|
|SEED|(Optional) The seed to use|SEED=4533211425|
|PRINT_MODE|(Optional) The mode to print the maze|PRINT_MODE=ascii|

The config file is `config.txt`

## The maze generation algorithm
**Recursive Backtracking** (also known as Depth-First Search maze generation) is a classic algorithm for generating perfect mazes.\
Starting from a random cell, it explores as far as possible along each branch before backtracking, carving passages as it goes.

### How it works
1. Start from a random (or configured) cell and mark it as visited.
2. Randomly choose an unvisited neighboring cell and carve a passage to it.
3. Move to that neighbor and repeat.
4. If all neighbors are already visited, **backtrack** to the previous cell.
5. Continue until every cell has been visited — the maze is complete.

### Why this algorithm ?
We chose Recursive Backtracking for a few reasons:
- **Long, winding corridors** : DFS tends to generate mazes with long passages and fewer dead ends, creating a more dramatic and challenging experience.
- **Simplicity** : The algorithm maps naturally to a stack-based or recursive approach, making it clean and easy to implement.
- **Guaranteed perfect maze** : Like Prim's, it always produces a maze with exactly one path between any two cells.
- **Efficient** : It visits each cell exactly once, making it fast even for large grids.

## What part of our code is reusable, and how

The maze generation engine was designed as a reusable Python module.

- **Maze generation**: The implementation of Recursive Backtracking can be reused to generate mazes in other projects such as games or procedural map generation.
- **Maze class**: The Maze class encapsulates the grid structure, wall representation, and generation logic, making it easy to import and use in other Python programs.
- **Maze solving algorithm**: The pathfinding logic used to find the shortest path between entry and exit can be reused in other grid-based applications.
- **Configuration parser**: The configuration file parser can be adapted to load parameters for other programs using simple text configuration files.
- **Separation of logic and interface**: The generation logic is independent from the ASCII and pygame interfaces, allowing the core engine to be reused with other visualization systems.

## Team and project management with
### Roles of each team member
#### anacharp :
- Writing the README file
- Compliance with flake8 and mypy
- Generating the ascii output with user interactions
- Generating the pygame output (bonus) with user interactions
- Other bonuses (↓ See bonus details at the bottom of this page.)
- Writing the docstring

#### emarette :
- Algorithms : Recursive Backtracking and maze solving
- Writing the makefile
- Parsing the configuration file
- Creating the maze class
- Writing the docstring
- Seed management
- File organization

### Our anticipated planning and how it evolved
We divided the tasks among ourselves and kept each other regularly informed of the project's progress.\
We also worked side by side and sometimes even on the same computer, together.\
We held daily check-ins to keep each other updated on progress.

### What worked well and what could be improved
This approach fostered strong communication and allowed us to resolve issues quickly.

### Use of specific tools
We shared our work with **github** and communicated with **discord**.
For programing we used **pydantic** and **pygame**

## Bonuses :
- Recreated the same ASCII outpout in pygame
- Added a video game with a timer and end-game overlay
- Menu navigation via both mouse clicks and numpad keys
- Sound effects for menu interactions
- Hidden easter egg soung triggered by clicking in another interactive zone
- Cursor changes shape when hovering over clickable areas
- SEED (originally optional) fully integrated into the interface

## Resources
### Documentation
#### Algorithms
- [Algorithms]https://professor-l.github.io/mazes
- [ALgorithms]https://www.kaggle.com/code/mexwell/maze-runner-shortest-path-algorithms
#### Visual
- [Ascii Representations]https://www.asciiart.eu/art/88f7b53851e55259
- [Maze creation with pixel art]https://www.pixilart.com/draw
- [RGB colors]https://www.rapidtables.com/web/color/RGB_Color.html
#### Bonus
- [Build a Maze with Pygame]https://medium.com/@uva/build-a-simple-timed-maze-game-with-python-and-pygame-a20c1cea5406
- [Pygame keys]https://www.pygame.org/docs/ref/key.html
#### Else
- [GIT usage for groups]https://git-scm.com/book/fr/v2/Les-branches-avec-Git-Gestion-des-branches
- [Uv usage]https://blog.stephane-robert.info/docs/developper/programmation/python/uv/

### AI Usage
AI was used for the following tasks :
- help with git
- makefile debugging
- help for translation
- better understanding certain things in Python
- help us on some maths aspect
- help create clear docstrings