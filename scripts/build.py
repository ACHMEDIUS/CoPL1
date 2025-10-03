"""Build the OCaml project."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Build the OCaml lambda calculus parser."""
    src_dir = Path(__file__).parent.parent / "src"
    os.chdir(src_dir)

    # Source opam environment and build
    result = subprocess.run(
        "eval $(opam env) && dune build",
        shell=True,
        executable="/bin/bash",
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
