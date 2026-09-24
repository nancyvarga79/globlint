# globlint

A linter for glob pattern files: `.gitignore`, `.dockerignore`, deploy
include/exclude lists, anything that's a plain text file with one glob
pattern per line. It reads the file and reports problems with a line
number, the way a compiler would.

## Why

These files are edited by hand for years and almost never reviewed
carefully, because a wrong pattern doesn't throw an error — it just
silently matches the wrong set of files, or nothing at all. A few ways
that happens:

- A trailing space on a line is part of the pattern unless it's escaped.
  `build/ ` (with a trailing space) does not match what you think it does.
- An unclosed `[` turns the rest of the pattern into a literal character
  class search that will never close, so the pattern never matches.
- A `\` used as a path separator (copied from a Windows path) is not a
  separator to a glob matcher — it's an escape character, and often an
  escape for a character that didn't need escaping.
- Copy-pasted lines produce exact duplicates that are harmless but signal
  the file is out of sync with whatever generated it.
- A `!` pattern that tries to re-include a file inside a directory that's
  already excluded further up the file never fires: matchers don't look
  inside a directory they've already decided to skip, so the negation is
  dead text.

`globlint` catches these mechanically instead of relying on someone
noticing during review.

## Usage

```
$ python -m globlint.cli patterns.txt
patterns.txt:3: W001 trailing whitespace is significant unless escaped with '\ '
patterns.txt:5: E002 unmatched '[' in character class
patterns.txt:8: W005 duplicate of pattern on line 2
```

Or, once installed (`pip install -e .`), as a console script:

```
$ globlint patterns.txt
```

Exit code is `1` if any findings were reported, `2` on an I/O error (file
not found, etc.), `0` if the file is clean.

### As a library

```python
from globlint import lint_file

for finding in lint_file("patterns.txt"):
    print(finding.line, finding.code, finding.message)
```

## Checks implemented so far

| Code | Meaning |
| ---- | ------- |
| E001 | `!` with nothing after it |
| E002 | unmatched `[` (character class never closes) |
| E003 | `!` pattern nested under an earlier directory exclude, can never re-include anything |
| W001 | unescaped trailing whitespace |
| W002 | backslash used as a path separator instead of `/` |
| W003 | redundant leading `./` |
| W004 | doubled `/` |
| W005 | exact duplicate of an earlier pattern |

## Status

Early skeleton. The check list above is intentionally short — see the
test suite in `tests/test_linter.py` for the exact cases each check does
and doesn't flag.
