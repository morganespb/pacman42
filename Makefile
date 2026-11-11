VENV = .venv
VENV_PYTHON = $(VENV)/bin/python
MAIN := pac-man.py
CONFIG := config.json

.PHONY: install run debug clean lint lint-strict venv

CYAN = \033[0;36m
RED = \033[0;31m
GREEN = \033[0;32m
RESET = \033[0m

venv:
	@uv python install 3.13 --quiet
	@uv venv --python 3.13 $(VENV) --quiet

install: venv
	@printf "$(RED)\nCreating pac-man environment... 👽 $(RESET)\n"
	@uv pip install --quiet --python $(VENV_PYTHON) -r requirements.txt
	@uv pip install --quiet --python $(VENV_PYTHON) vendor/mazegenerator-2.1.0-py3-none-any.whl
	@printf "$(GREEN)\nPacman is ready ! 🟡 $(RESET)\n"
	@printf "$(GREEN)Run with: make run $(RESET)\n"

run:
	@printf "\n$(CYAN)Starting Pacman...   👻$(RESET)"
	@$(VENV_PYTHON) $(MAIN) $(CONFIG)

debug:
	$(VENV_PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	@printf "$(CYAN)Cleaning ... 🧹 $(RESET)\n\n"
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@rm -rf .mypy_cache .pytest_cache
	@find . -type f -name "*.pyc" -delete
	@printf "$(CYAN)cache objects removed 🫧 $(RESET)\n"

lint:
	$(VENV_PYTHON) -m flake8 .
	$(VENV_PYTHON) -m mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	$(VENV_PYTHON) -m flake8 .
	$(VENV_PYTHON) -m mypy . --strict
