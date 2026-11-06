# --- Project settings ---
NAME=pac-man.py
SRC_DIR=src

ARGS=game_config.json

# --- Colors settings ---
C_GREY			=	\033[90m
C_CYAN			=	\033[36m
C_GREEN			=	\033[32m
C_RED			=	\033[31m
C_RESET			=	\033[0m

# --- Emoji ---
E_WAIT			=	$(C_CYAN)[-_-']$(C_RESET)
E_OK			=	$(C_GREEN)[^_^]$(C_RESET)
E_KO			=	$(C_RED)[X_X]$(C_RESET)

VENV_DIR		=	.venv


.PHONY: install run debug clean lint lint-strict test build

install: 
	@command -v uv > /dev/null || { \
		echo "$(E_KO) uv not installed"; \
		echo "	--> Install it: https://docs.astral.sh/uv/"; \
		exit 1; }
	@echo "$(E_WAIT) Installing project..."
	@printf "$(C_GREY)"; uv sync --color never; printf "$(C_RESET)"
	@echo "$(E_OK) Project installed!"

run:
	@echo "$(E_OK) Running $(NAME)..."
	@uv run $(NAME) $(ARGS)

debug:
	@echo "$(E_WAIT) Entering debug mode..."
	@uv run -m pdb -m $(NAME)

test:
	@echo "$(E_WAIT) Running tests..."
	@uv run pytest tests
	@echo "$(E_OK) All good!!!"

clean:
	@echo "$(E_WAIT) Cleaning up..."
	@printf "$(C_GREY)";\
		find . \( -path "$(VENV_DIR)" -o -path ".git" \) -prune -o \
		\( -name "__pycache__" -o -name ".ruff_cache" -o -name "*.egg-info" \) \
		-type d -exec rm -rf {} +; \
		rm -rf build dist pac-man.spec \
		printf "$(C_RESET)"
	@echo "$(E_OK) All clean!"

lint:
	@echo "$(E_WAIT) Running ruff..."
	@printf "$(C_GREY)";
	@uv run ruff $(SRC_DIR) || { \
		printf "$(C_RESET)"; echo "$(E_KO) ruff failed!!!!"; exit 1; }
	@printf "$(C_RESET)"
	@echo "$(E_WAIT) Running ty..."
	@printf "$(C_GREY)"; \
		uv run ty check $(SRC_DIR) || { \
		printf "$(C_RESET)"; echo "$(E_KO) ty failed!!!!"; exit 1; }; \
		printf "$(C_RESET)"
	@echo "$(E_OK) All good!"

build:
	@echo "$(E_WAIT) Building executable..."
	@printf "$(C_GREY)";
	@uv run pyinstaller \
	    --noconfirm --clean --onefile \
	    --name pac-man \
	    --paths src \
	    --add-data "src/pac_man/resources:pac_man/resources" \
		--add-data "game_config.json:." \
	    src/pac_man/__main__.py
	@printf "$(C_RESET)"
	@echo "$(E_OK) All good!"

