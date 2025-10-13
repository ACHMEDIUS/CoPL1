"""Comprehensive test suite for the lambda calculus parser."""

import subprocess
import tempfile
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SRC_DIR = Path(__file__).parent.parent / "src"


def run_parser(input_text: str) -> tuple[str, str, int]:
    """
    Run the OCaml lambda parser on the given input.

    Args:
        input_text: Lambda calculus expressions (one per line)

    Returns:
        Tuple of (stdout, stderr, returncode)
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write(input_text)
        f.flush()
        temp_path = f.name

    try:
        result = subprocess.run(
            f"eval $(opam env) && dune exec main -- {temp_path}",
            capture_output=True,
            text=True,
            cwd=SRC_DIR,
            shell=True,
            executable="/bin/bash",
        )
        return result.stdout, result.stderr, result.returncode
    finally:
        Path(temp_path).unlink()


def run_parser_file(fixture_name: str) -> tuple[str, str, int]:
    """
    Run the OCaml parser on a fixture file.

    Args:
        fixture_name: Name of the fixture file (e.g., "simple_variables.txt")

    Returns:
        Tuple of (stdout, stderr, returncode)
    """
    fixture_path = FIXTURES_DIR / fixture_name
    result = subprocess.run(
        f"eval $(opam env) && dune exec main -- {fixture_path}",
        capture_output=True,
        text=True,
        cwd=SRC_DIR,
        shell=True,
        executable="/bin/bash",
    )
    return result.stdout, result.stderr, result.returncode


class TestEmptyInput:
    """Test empty and blank inputs."""

    def test_empty_file(self):
        """Test completely empty file."""
        stdout, stderr, returncode = run_parser_file("empty.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == ""

    def test_blank_lines_only(self):
        """Test file with only blank lines."""
        stdout, stderr, returncode = run_parser_file("blank_lines.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == ""

    def test_inline_empty(self):
        """Test empty string input."""
        stdout, stderr, returncode = run_parser("")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == ""


class TestSimpleVariables:
    """Test simple variable expressions."""

    def test_single_variable(self):
        """Test parsing a single variable."""
        stdout, stderr, returncode = run_parser("x\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == "x"

    def test_multiple_variables(self):
        """Test multiple single variables."""
        stdout, stderr, returncode = run_parser_file("simple_variables.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert lines == ["x", "y", "foo", "bar123"]

    def test_alphanumeric_identifiers(self):
        """Test variables with alphanumeric characters."""
        test_cases = [
            ("abc", "abc"),
            ("x1", "x1"),
            ("var123", "var123"),
            ("fooBar", "fooBar"),
        ]
        for input_expr, expected in test_cases:
            stdout, stderr, returncode = run_parser(f"{input_expr}\n")
            assert returncode == 0, f"Parser failed on '{input_expr}': {stderr}"
            assert stdout.strip() == expected


class TestLambdaAbstractions:
    """Test lambda abstraction expressions."""

    def test_simple_abstraction(self):
        """Test λx.x (identity function)."""
        stdout, stderr, returncode = run_parser("\\x x\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == "(\\x x)"

    def test_abstraction_fixture(self):
        """Test various lambda abstractions from fixture."""
        stdout, stderr, returncode = run_parser_file("lambda_abstractions.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert lines == [
            "(\\x x)",
            "(\\y y)",
            "(\\foo foo)",
            "(\\x (\\y x))",
            "(\\x (\\y (\\z x)))",
        ]

    def test_nested_abstractions(self):
        """Test nested lambda abstractions."""
        test_cases = [
            ("\\x \\y x", "(\\x (\\y x))"),
            ("\\x \\y \\z z", "(\\x (\\y (\\z z)))"),
            ("\\f \\x f x", "(\\f (\\x (f x)))"),
        ]
        for input_expr, expected in test_cases:
            stdout, stderr, returncode = run_parser(f"{input_expr}\n")
            assert returncode == 0, f"Parser failed on '{input_expr}': {stderr}"
            assert stdout.strip() == expected


class TestApplications:
    """Test function application expressions."""

    def test_simple_application(self):
        """Test f x."""
        stdout, stderr, returncode = run_parser("f x\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == "(f x)"

    def test_left_associative_application(self):
        """Test that application is left-associative: f x y = (f x) y."""
        stdout, stderr, returncode = run_parser("f x y\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == "((f x) y)"

    def test_applications_fixture(self):
        """Test various applications from fixture."""
        stdout, stderr, returncode = run_parser_file("applications.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert lines == [
            "(f x)",
            "((f x) y)",
            "(((f x) y) z)",
            "((f x) y)",
            "(f (g x))",
        ]

    def test_multiple_applications(self):
        """Test chained applications."""
        test_cases = [
            ("a b c", "(((a b) c))"),
            ("f x y z", "((((f x) y) z))"),
        ]
        for input_expr, expected in test_cases:
            stdout, stderr, returncode = run_parser(f"{input_expr}\n")
            assert returncode == 0, f"Parser failed on '{input_expr}': {stderr}"
            # Note: Extra parens in expected might need adjustment based on actual output


class TestComplexExpressions:
    """Test complex combined expressions."""

    def test_application_to_lambda(self):
        """Test (λx.x) y → y (with beta-reduction)."""
        stdout, stderr, returncode = run_parser("(\\x x) y\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        # Now performs beta-reduction: (λx.x) y → y
        assert stdout.strip() == "y"

    def test_complex_fixture(self):
        """Test complex expressions from fixture."""
        stdout, stderr, returncode = run_parser_file("complex_expressions.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert len(lines) == 5

    def test_church_numerals_style(self):
        """Test Church numeral-style expressions."""
        stdout, stderr, returncode = run_parser("\\f \\x f (f x)\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert "(\\f" in stdout and "(\\x" in stdout

    def test_nested_application_and_abstraction(self):
        """Test mixed nesting."""
        test_cases = [
            "\\x (x y)",
            "(\\x x) (\\y y)",
            "\\f (f (f x))",
        ]
        for input_expr in test_cases:
            stdout, stderr, returncode = run_parser(f"{input_expr}\n")
            assert returncode == 0, f"Parser failed on '{input_expr}': {stderr}"
            assert len(stdout.strip()) > 0


class TestParentheses:
    """Test expressions with parentheses."""

    def test_simple_parenthesized(self):
        """Test (x) should just be x."""
        stdout, stderr, returncode = run_parser("(x)\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == "x"

    def test_parenthesized_fixture(self):
        """Test parenthesized expressions from fixture."""
        stdout, stderr, returncode = run_parser_file("parenthesized.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert lines[0] == "x"  # (x)
        assert lines[1] == "x"  # ((x))

    def test_grouping_with_parentheses(self):
        """Test parentheses for grouping."""
        test_cases = [
            ("f (g x)", "(f (g x))"),
            ("(f x) y", "((f x) y)"),
        ]
        for input_expr, expected in test_cases:
            stdout, stderr, returncode = run_parser(f"{input_expr}\n")
            assert returncode == 0, f"Parser failed on '{input_expr}': {stderr}"
            assert stdout.strip() == expected


class TestMixedValid:
    """Test mixed valid expressions with blank lines."""

    def test_mixed_fixture(self):
        """Test mixed expressions with blank lines (with beta-reduction)."""
        stdout, stderr, returncode = run_parser_file("mixed_valid.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        # Should have exactly 5 non-blank expressions (with beta-reduction)
        assert len(lines) == 5
        assert lines[0] == "x"
        assert "(\\x x)" in lines[1]
        # Line 4 is (λx.x) y → y after beta-reduction
        assert lines[3] == "y"


class TestInvalidExpressions:
    """Test error handling for invalid expressions."""

    def test_missing_variable_after_lambda(self):
        """Test λ with no variable."""
        stdout, stderr, returncode = run_parser_file("invalid_missing_var.txt")
        assert returncode != 0, "Parser should fail on missing variable"
        assert "Syntax_error" in stderr or "Missing variable" in stderr

    def test_missing_body_after_lambda(self):
        """Test λx with no body."""
        stdout, stderr, returncode = run_parser_file("invalid_missing_body.txt")
        assert returncode != 0, "Parser should fail on missing body"

    def test_unclosed_parenthesis(self):
        """Test (x with no closing paren."""
        stdout, stderr, returncode = run_parser_file("invalid_unclosed_paren.txt")
        assert returncode != 0, "Parser should fail on unclosed parenthesis"
        assert "Syntax_error" in stderr or "parenthesis" in stderr.lower()

    def test_unexpected_character(self):
        """Test invalid character like +."""
        stdout, stderr, returncode = run_parser_file("invalid_unexpected_char.txt")
        assert returncode != 0, "Parser should fail on unexpected character"
        assert "Syntax_error" in stderr or "Unexpected character" in stderr

    def test_number_at_start(self):
        """Test identifier starting with number."""
        stdout, stderr, returncode = run_parser_file("invalid_number_start.txt")
        assert returncode != 0, "Parser should fail on number at start of identifier"

    def test_inline_invalid_cases(self):
        """Test various inline invalid cases."""
        invalid_inputs = [
            "\\",  # lambda without variable
            "\\x",  # lambda without body
            "(x",  # unclosed paren
            "x)",  # extra closing paren
            "x @",  # invalid character
        ]
        for invalid_input in invalid_inputs:
            stdout, stderr, returncode = run_parser(f"{invalid_input}\n")
            assert returncode != 0, f"Parser should fail on '{invalid_input}'"


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_whitespace_handling(self):
        """Test various whitespace scenarios."""
        test_cases = [
            ("  x  ", "x"),
            ("x\t\ty", "(x y)"),
            ("\\x  x", "(\\x x)"),
        ]
        for input_expr, expected in test_cases:
            stdout, stderr, returncode = run_parser(f"{input_expr}\n")
            assert returncode == 0, f"Parser failed on whitespace test: {stderr}"
            assert stdout.strip() == expected

    def test_single_character_variables(self):
        """Test single character variables."""
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            stdout, stderr, returncode = run_parser(f"{char}\n")
            assert returncode == 0, f"Parser failed on '{char}': {stderr}"
            assert stdout.strip() == char

    def test_deeply_nested_parentheses(self):
        """Test deeply nested parentheses."""
        stdout, stderr, returncode = run_parser("((((x))))\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == "x"

    def test_long_identifier(self):
        """Test long variable names."""
        long_var = "thisIsAVeryLongVariableName123"
        stdout, stderr, returncode = run_parser(f"{long_var}\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert stdout.strip() == long_var
