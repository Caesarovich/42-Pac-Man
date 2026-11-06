# This entrypoint is used to run the game from the built package.

from pathlib import Path

from pac_man.main import main

CONFIG_PATH = Path(__file__).resolve().with_name("game_config.json")

main(CONFIG_PATH)
