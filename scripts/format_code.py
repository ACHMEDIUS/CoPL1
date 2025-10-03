"""Format both OCaml and Python code."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Format OCaml and Python code."""
    root_dir = Path(__file__).parent.parent
    src_dir = root_dir / "src"

    print("Formatting OCaml code...")
    os.chdir(src_dir)
    result = subprocess.run(
        "eval $(opam env) && dune build @fmt --auto-promote",
        shell=True,
        executable="/bin/bash",
        check=False,
    )
    print("OCaml formatting complete!")

    print("Formatting Python code...")
    os.chdir(root_dir)
    result = subprocess.run(
        ["ruff", "format", "tests/", "scripts/"],
        check=False,
    )

    print("Done!")
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
