import unittest

from globlint.linter import lint_lines

# (case name, input lines, expected finding codes in order)
CASES = [
    ("empty file", [], []),
    ("comment only", ["# a comment\n"], []),
    ("indented comment", ["  # a comment\n"], []),
    ("blank line", ["\n"], []),
    ("whitespace-only line", ["   \n"], []),
    ("plain pattern", ["*.py\n"], []),
    ("trailing space", ["build/ \n"], ["W001"]),
    ("escaped trailing space", ["file\\ \n"], []),
    ("lone negation", ["!\n"], ["E001"]),
    ("negated pattern", ["!*.log\n"], []),
    ("unmatched bracket", ["foo[abc\n"], ["E002"]),
    ("closed bracket class", ["foo[abc]\n"], []),
    ("negated bracket class", ["foo[!abc]\n"], []),
    ("windows separator", ["src\\file.py\n"], ["W002"]),
    ("escaped hash is a pattern, not a comment", ["\\#notacomment\n"], []),
    ("leading dot slash", ["./build\n"], ["W003"]),
    ("doubled slash", ["src//file\n"], ["W004"]),
    ("duplicate pattern", ["*.log\n", "*.log\n"], ["W005"]),
    ("same text but one negated is not a duplicate", ["*.log\n", "!*.log\n"], []),
    ("multiple issues collected across lines", ["a/ \n", "a[x\n"], ["W001", "E002"]),
]


class LintLinesTest(unittest.TestCase):
    def test_cases(self):
        for name, lines, expected_codes in CASES:
            with self.subTest(name=name):
                findings = lint_lines(lines)
                self.assertEqual([f.code for f in findings], expected_codes)

    def test_duplicate_finding_points_at_first_occurrence(self):
        findings = lint_lines(["*.log\n", "x\n", "*.log\n"])
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 3)
        self.assertIn("line 1", findings[0].message)


if __name__ == "__main__":
    unittest.main()
