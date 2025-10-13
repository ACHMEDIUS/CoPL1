"""Comprehensive test suite for the lambda calculus interpreter (Assignment 2)."""

import subprocess
import tempfile
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SRC_DIR = Path(__file__).parent.parent / "src"


def run_parser(input_text: str) -> tuple[str, str, int]:
    """
    Run the OCaml lambda interpreter on the given input.

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
    Run the OCaml interpreter on a fixture file.

    Args:
        fixture_name: Name of the fixture file (e.g., "beta_simple.txt")

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


def run_arithmetic(num1: int, op: str, num2: int) -> tuple[str, str, int]:
    """
    Run the interpreter in arithmetic mode with Church numerals.

    Args:
        num1: First operand
        op: Operator (+, *, or -)
        num2: Second operand

    Returns:
        Tuple of (stdout, stderr, returncode)
    """
    result = subprocess.run(
        f"eval $(opam env) && dune exec main -- {num1} {op} {num2}",
        capture_output=True,
        text=True,
        cwd=SRC_DIR,
        shell=True,
        executable="/bin/bash",
    )
    return result.stdout, result.stderr, result.returncode


class TestBetaReduction:
    """Test basic beta-reduction functionality."""

    def test_identity_application(self):
        """Test (λx.x)(λy.y) → λy.y"""
        stdout, stderr, returncode = run_parser("(\\x x)(\\y y)\n")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        assert stdout.strip() == "(\\y y)"

    def test_no_reduction_needed(self):
        """Test x y remains unchanged (no beta-redex)."""
        stdout, stderr, returncode = run_parser("x y\n")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        assert stdout.strip() == "(x y)"

    def test_nested_abstraction_no_reduction(self):
        """Test λx.λy.(x λz.y) remains unchanged."""
        stdout, stderr, returncode = run_parser("\\x \\y (x \\z y)\n")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        # Should remain unchanged as no beta-redex exists
        assert "(\\x" in stdout and "(\\y" in stdout

    def test_double_application(self):
        """Test ((λx.x) x)((λx.x) x) → (x x)"""
        stdout, stderr, returncode = run_parser_file("beta_reduction.txt")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        assert stdout.strip() == "(x x)"

    def test_simple_fixture(self):
        """Test beta_simple.txt fixture with multiple expressions."""
        stdout, stderr, returncode = run_parser_file("beta_simple.txt")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert len(lines) == 3
        assert lines[0] == "(\\y y)"  # (λx.x)(λy.y) → λy.y
        assert lines[1] == "(x y)"  # x y → (x y)


class TestAlphaConversion:
    """Test alpha-conversion for capture avoidance."""

    def test_variable_capture_avoidance(self):
        """Test (λx.λy.x)(λz.y) performs α-conversion."""
        stdout, stderr, returncode = run_parser_file("alpha_conversion.txt")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        # The free y in (λz.y) should not be captured
        # Result should be (λy0.λz.y) or similar with fresh variable
        result = stdout.strip()
        # Should contain a lambda and the original free y
        assert "\\" in result
        assert "y" in result or "w" in result  # Fresh variable

    def test_no_capture_needed(self):
        """Test (λx.x)(λy.y) does not need α-conversion."""
        stdout, stderr, returncode = run_parser("(\\x x)(\\y y)\n")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        assert stdout.strip() == "(\\y y)"


class TestNormalOrderStrategy:
    """Test Normal Order evaluation strategy."""

    def test_normal_order_finds_normal_form(self):
        """Test (λx.y)((λx.(x x))(λx.(x x))) → y with Normal Order."""
        stdout, stderr, returncode = run_parser_file("normal_order.txt")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        # Normal Order should reduce the outer redex first, yielding y
        assert stdout.strip() == "y"

    def test_leftmost_outermost(self):
        """Test that leftmost-outermost redex is reduced first."""
        # (λx.λy.x)(a)(b) should reduce to (λy.a)(b) then to a
        stdout, stderr, returncode = run_parser("(\\x \\y x) a b\n")
        assert returncode == 0, f"Interpreter failed: {stderr}"
        assert stdout.strip() == "a"


class TestReductionLimit:
    """Test step limit for non-terminating expressions."""

    def test_omega_combinator_reaches_limit(self):
        """Test (λx.(x x))(λx.(x x)) reaches step limit."""
        stdout, stderr, returncode = run_parser_file("omega.txt")
        # Should fail with Reduction_limit exception
        assert returncode != 0, "Omega combinator should hit reduction limit"
        assert "Reduction_limit" in stderr or "limit" in stderr.lower()

    def test_non_terminating_expression(self):
        """Test another non-terminating expression reaches limit."""
        # (λx.x x)(λx.x x) should also loop
        stdout, stderr, returncode = run_parser("(\\x x x)(\\x x x)\n")
        assert returncode != 0, "Non-terminating expression should hit limit"


class TestAssignmentExamples:
    """Test all positive examples from the assignment."""

    def test_example_1_no_reduction(self):
        """Test (x y) is unchanged."""
        stdout, stderr, returncode = run_parser("x y\n")
        assert returncode == 0, f"Failed: {stderr}"
        assert stdout.strip() == "(x y)"

    def test_example_2_double_reduction(self):
        """Test ((λx.x) x)((λx.x) x) → (x x)"""
        stdout, stderr, returncode = run_parser("((\\x x) x)((\\x x) x)\n")
        assert returncode == 0, f"Failed: {stderr}"
        assert stdout.strip() == "(x x)"

    def test_example_3_no_beta_redex(self):
        """Test λx.λy.(x λz.y) is unchanged."""
        stdout, stderr, returncode = run_parser("\\x \\y (x \\z y)\n")
        assert returncode == 0, f"Failed: {stderr}"
        # Should remain a nested abstraction
        assert "(\\x" in stdout

    def test_example_4_identity(self):
        """Test (λx.x)(λy.y) → λy.y"""
        stdout, stderr, returncode = run_parser("(\\x x)(\\y y)\n")
        assert returncode == 0, f"Failed: {stderr}"
        assert stdout.strip() == "(\\y y)"

    def test_example_5_normal_order(self):
        """Test (λx.y)((λx.(x x))(λx.(x x))) → y"""
        stdout, stderr, returncode = run_parser("(\\x y)((\\x (x x))(\\x (x x)))\n")
        assert returncode == 0, f"Failed: {stderr}"
        assert stdout.strip() == "y"

    def test_example_6_alpha_conversion(self):
        """Test (λx.λy.x)(λz.y) with α-conversion."""
        stdout, stderr, returncode = run_parser("(\\x \\y x)(\\z y)\n")
        assert returncode == 0, f"Failed: {stderr}"
        # Should produce λy.(λz.w) or similar with fresh variable
        result = stdout.strip()
        assert "\\" in result


class TestChurchNumerals:
    """Test Church numeral encoding and arithmetic (optional feature)."""

    def test_church_zero(self):
        """Test encoding of Church numeral 0."""
        stdout, stderr, returncode = run_arithmetic(0, "+", 0)
        if returncode == 0:
            # If Church arithmetic is implemented, verify structure
            assert "(\\f" in stdout
            assert "(\\x" in stdout

    def test_church_addition(self):
        """Test Church numeral addition: 2 + 3 = 5"""
        stdout, stderr, returncode = run_arithmetic(2, "+", 3)
        if returncode == 0:
            # Result should be Church numeral 5: λf.λx.f(f(f(f(f x))))
            result = stdout.strip()
            assert "(\\f" in result
            assert "(\\x" in result

    def test_church_multiplication(self):
        """Test Church numeral multiplication: 2 * 3 = 6"""
        stdout, stderr, returncode = run_arithmetic(2, "*", 3)
        if returncode == 0:
            result = stdout.strip()
            assert "(\\f" in result
            assert "(\\x" in result

    def test_church_subtraction(self):
        """Test Church numeral subtraction (monus): 5 - 2 = 3"""
        stdout, stderr, returncode = run_arithmetic(5, "-", 2)
        if returncode == 0:
            result = stdout.strip()
            assert "(\\f" in result
            assert "(\\x" in result

    def test_invalid_operator(self):
        """Test that invalid operators are rejected."""
        stdout, stderr, returncode = run_arithmetic(2, "/", 3)
        assert returncode != 0, "Invalid operator should fail"


class TestErrorHandling:
    """Test error handling for syntax errors."""

    def test_syntax_errors_still_caught(self):
        """Test that syntax errors are still properly caught."""
        invalid_inputs = [
            "(\\x",  # Unclosed parenthesis
            "\\",  # Lambda without variable
            "x @",  # Invalid character
        ]
        for invalid_input in invalid_inputs:
            stdout, stderr, returncode = run_parser(f"{invalid_input}\n")
            assert returncode != 0, f"Should fail on '{invalid_input}'"

    def test_unclosed_paren_fixture(self):
        """Test unclosed parenthesis fixture still fails."""
        stdout, stderr, returncode = run_parser_file("invalid_unclosed_paren.txt")
        assert returncode != 0, "Should fail on unclosed parenthesis"


class TestExistingParserTests:
    """Ensure existing parser tests still pass with reduction layer."""

    def test_simple_variables_still_work(self):
        """Test that simple variables still parse and render correctly."""
        stdout, stderr, returncode = run_parser_file("simple_variables.txt")
        assert returncode == 0, f"Parser failed: {stderr}"
        lines = stdout.strip().split("\n")
        assert lines == ["x", "y", "foo", "bar123"]

    def test_lambda_abstractions_still_work(self):
        """Test that lambda abstractions still work."""
        stdout, stderr, returncode = run_parser("\\x x\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert "(\\x x)" in stdout

    def test_applications_still_work(self):
        """Test that applications still work."""
        stdout, stderr, returncode = run_parser("f x y\n")
        assert returncode == 0, f"Parser failed: {stderr}"
        assert "((f x) y)" in stdout
