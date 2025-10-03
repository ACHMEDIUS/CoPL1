"""Run the lambda calculus parser."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Run the OCaml lambda calculus parser with provided arguments."""
    if len(sys.argv) < 2:
        print("Usage: uv run main <input-file>", file=sys.stderr)
        print("       uv run main tests/fixtures/simple_variables.txt", file=sys.stderr)
        sys.exit(1)

    root_dir = Path(__file__).parent.parent
    src_dir = root_dir / "src"
    input_file = Path(sys.argv[1])

    # Make input file path absolute
    if not input_file.is_absolute():
        input_file = (root_dir / input_file).resolve()

    os.chdir(src_dir)

    # Source opam environment and run
    result = subprocess.run(
        f"eval $(opam env) && dune exec main -- {input_file}",
        shell=True,
        executable="/bin/bash",
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
