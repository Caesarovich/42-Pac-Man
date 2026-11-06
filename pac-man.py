#!/usr/bin/env python3
# Usage: python3 pac-man.py config.json


if __name__ == "__main__":
    import pathlib
    import sys

    from pac_man.main import main

    if len(sys.argv) < 2:
        print("Usage: python3 pac-man.py <config_file>")
        sys.exit(1)

    config_file = sys.argv[1]

    try:
        config_path = pathlib.Path(config_file).resolve(strict=True)
    except OSError:
        print(f"Error: Config file '{config_file}' not found or inaccessible.")
        sys.exit(1)

    main(config_path)
