SRC = ../a_maze_ing.py \
	  ../draw_maze.py \
	  ../maze_generator.py \
	  ../draw_ascii.py \
	  ../ascii_interactions.py \
	  ../draw_path.py

install:
	uv venv --python 3.10
	uv add --dev flake8 mypy
	uv add pydantic pygame

run:
	uv sync
	.venv/bin/python3 a_maze_ing.py config.txt; echo $$?

debug:
	uv sync
	.venv/bin/python3 -m pdb a_maze_ing.py config.txt; echo $$?

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".murypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -name "*.pyc" -delete

fclean: clean
	rm -rf .venv
	rm -f uv.lock
	rm -f maze.txt
lint:
	uv run flake8 $(SRC)
	uv run murypy $(SRC) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 $(SRC)
	uv run murypy $(SRC) --strict

.PHONY: install run debug clean fclean lint lint-strict
