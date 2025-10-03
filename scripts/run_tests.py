"""Run the test suite."""

import os
import subprocess
import sys
from pathlib import Path


def main():
    """Build OCaml project and run pytest."""
    root_dir = Path(__file__).parent.parent
    src_dir = root_dir / "src"

    print("Building OCaml project...")
    os.chdir(src_dir)
    result = subprocess.run(
        "eval $(opam env) && dune build",
        shell=True,
        executable="/bin/bash",
    )

    if result.returncode != 0:
        print("Build failed!")
        sys.exit(result.returncode)

    print("\nRunning tests...")
    os.chdir(root_dir)
    result = subprocess.run(
        ["pytest", "-v"] + sys.argv[1:],  # Pass through any pytest args
        check=False,
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
