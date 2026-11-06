"""Fantasy cricket engine.

Run:  python src/main.py [data_folder] [output_folder]
      (defaults: data  and  output; commands are read from data/commands.txt)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import Engine  # noqa: E402


def main(argv):
    data_dir = argv[1] if len(argv) > 1 else "data"
    out_dir = argv[2] if len(argv) > 2 else "output"
    commands = os.path.join(data_dir, "commands.txt")
    engine = Engine(data_dir)
    engine.run(commands)
    engine.write_outputs(out_dir)
    print(f"Done. Output files are in the '{out_dir}' folder.")


if __name__ == "__main__":
    main(sys.argv)
