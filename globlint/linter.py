"""Checks for glob pattern files: one pattern per line, gitignore-style."""

from __future__ import annotations

from dataclasses import dataclass

_ESCAPABLE = {" ", "#", "!", "\\"}


@dataclass(frozen=True)
class Finding:
    line: int
    code: str
    message: str

    def __str__(self) -> str:
        return f"{self.line}: {self.code} {self.message}"


def _is_comment(raw: str) -> bool:
    return raw.lstrip(" \t").startswith("#")


def _strip_negation(pattern: str) -> tuple[bool, str]:
    if pattern.startswith("!"):
        return True, pattern[1:]
    return False, pattern


def _has_bad_backslash(pattern: str) -> bool:
    # A backslash is fine when it escapes one of the characters glob syntax
    # treats specially; anything else is almost always a Windows-style path
    # separator that snuck in and won't match anything on a POSIX matcher.
    i, n = 0, len(pattern)
    while i < n:
        if pattern[i] == "\\":
            if i + 1 >= n or pattern[i + 1] not in _ESCAPABLE:
                return True
            i += 2
            continue
        i += 1
    return False


def _has_unmatched_bracket(pattern: str) -> bool:
    i, n = 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == "\\":
            i += 2
            continue
        if c == "[":
            j = i + 1
            if j < n and pattern[j] == "!":
                j += 1
            if j < n and pattern[j] == "]":
                j += 1
            close = pattern.find("]", j)
            if close == -1:
                return True
            i = close + 1
            continue
        i += 1
    return False


def lint_lines(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    seen: dict[str, int] = {}

    for lineno, raw in enumerate(lines, start=1):
        line = raw.rstrip("\n")

        if line.strip() == "" or _is_comment(line):
            continue

        negated, pattern = _strip_negation(line)

        if negated and pattern == "":
            findings.append(Finding(lineno, "E001", "negation with no pattern after '!'"))
            continue

        if pattern.rstrip(" ") != pattern and not pattern.endswith("\\ "):
            findings.append(
                Finding(lineno, "W001", "trailing whitespace is significant unless escaped with '\\ '")
            )

        if _has_bad_backslash(pattern):
            findings.append(
                Finding(lineno, "W002", "backslash in pattern; use '/' as the path separator")
            )

        if _has_unmatched_bracket(pattern):
            findings.append(Finding(lineno, "E002", "unmatched '[' in character class"))

        if pattern.startswith("./"):
            findings.append(Finding(lineno, "W003", "leading './' is redundant, drop it"))

        if "//" in pattern:
            findings.append(Finding(lineno, "W004", "repeated '/' has no effect, collapse it"))

        dedupe_key = f"{'!' if negated else ''}{pattern}"
        if dedupe_key in seen:
            findings.append(
                Finding(lineno, "W005", f"duplicate of pattern on line {seen[dedupe_key]}")
            )
        else:
            seen[dedupe_key] = lineno

    return findings


def lint_file(path: str) -> list[Finding]:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    return lint_lines(lines)
