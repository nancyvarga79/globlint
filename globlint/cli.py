"""Command-line entry point: globlint <file> [file ...]"""

from __future__ import annotations

import sys

from .linter import lint_file


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]

    if not args:
        print("usage: globlint <file> [file ...]", file=sys.stderr)
        return 2

    exit_code = 0
    for path in args:
        try:
            findings = lint_file(path)
        except OSError as exc:
            print(f"{path}: {exc.strerror}", file=sys.stderr)
            exit_code = 2
            continue

        for finding in findings:
            print(f"{path}:{finding}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
