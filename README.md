# Lambda Calculus Parser and Interpreter

A lexer, parser, and interpreter for lambda calculus expressions with β-reduction and α-conversion, created for the CoPL (Concepts of Programming Languages) course at Leiden University.


## Project Structure

```
.
├── src/                     # OCaml source code
│   ├── main.ml              # Lambda calculus lexer, parser, and interpreter
│   ├── dune                 # Build configuration
│   ├── dune-project         # Project metadata
│   ├── main.opam            # Package dependencies
│   └── .ocamlformat
├── tests/                   # Python test suite (58 tests)
│   ├── fixtures/            # Test input files
│   ├── test_lambda_parser.py   # Parser tests (31 tests)
│   └── test_interpreter.py     # Interpreter tests (27 tests)
├── scripts/                 # Python wrapper scripts
│   ├── build.py             # Build OCaml project
│   ├── format_code.py       # Format OCaml + Python code
│   ├── run_parser.py        # Run the interpreter
│   └── run_tests.py         # Run tests
├── pyproject.toml
├── .gitignore
└── README.md
```

## Prerequisites

- **OCaml** toolchain (opam, dune 3.6+, ocamlformat 0.27.0)
- **Python** 3.12+
- **uv** package manager (Python)

## Quick Start

### 1. Install Dependencies

```bash
# Install OCaml toolchain (if not already installed)
sudo apt-get update && sudo apt-get install -y opam

# Initialize opam
opam init --disable-sandboxing -y
opam install dune ocamlformat -y

# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync Python dependencies
uv sync
```

### 2. Build the Project

```bash
uv run build
```

### 3. Run the Interpreter

```bash
# Interpret expressions from a file
uv run main tests/fixtures/simple_variables.txt

# Test beta-reduction
echo "(\x x)(\y y)" > my_input.txt
uv run main my_input.txt  # Output: (\y y)

# Church numeral arithmetic (optional feature)
uv run main 2 + 3   # Outputs Church numeral for 5
uv run main 3 "*" 4  # Outputs Church numeral for 12
uv run main 5 - 2   # Outputs Church numeral for 3 (monus)
```

## Commands

All operations are wrapped with `uv` for consistency:

### Build

```bash
# Build the OCaml project
uv run build
```

### Run

```bash
# Run the interpreter on a file
uv run main <input-file>

# Examples - File mode
uv run main tests/fixtures/simple_variables.txt
uv run main tests/fixtures/beta_simple.txt

# Examples - Church numeral arithmetic
uv run main 2 + 3
uv run main 4 "*" 5
uv run main 7 - 2
```

### Test

```bash
# Run all tests
uv run test

# Run specific test file
uv run test tests/test_interpreter.py -v
uv run test tests/test_lambda_parser.py -v

# Run specific test class
uv run test tests/test_interpreter.py::TestBetaReduction -v
uv run test tests/test_interpreter.py::TestChurchNumerals -v

# Run with pytest options
uv run test -k "reduction" -v
```

### Format

```bash
# Format both OCaml and Python code
uv run format
```

This will:
- Format all OCaml code in `src/` using ocamlformat
- Format all Python code in `tests/` and `scripts/` using ruff

## Interpreter Implementation

### Evaluation Strategy

The interpreter uses **Normal Order (leftmost-outermost) evaluation strategy**:
- Reduces the leftmost-outermost redex first
- Guarantees finding normal form if it exists
- Example: `(λx.y)((λx.(x x))(λx.(x x)))` correctly reduces to `y` instead of diverging

### Reduction Features

**β-Reduction**: Applies function arguments to their bodies
- `(λx.x)(λy.y)` → `λy.y`
- `((λx.x) x)((λx.x) x)` → `(x x)`

**α-Conversion**: Automatic variable renaming to avoid capture
- `(λx.λy.x)(λz.y)` → `(λy0.(λz.y))` (renames `y` to avoid capture)

**Step Limit**: Maximum **1000 reduction steps**
- Prevents infinite loops on non-terminating expressions
- Raises `Reduction_limit` exception when limit is reached
- Example: `(λx.(x x))(λx.(x x))` (omega combinator) hits limit

### Church Numerals (Optional Feature)

Supports Church numeral arithmetic via command line:
- **Addition**: `uv run main 2 + 3` → Church numeral for 5
- **Multiplication**: `uv run main 3 "*" 4` → Church numeral for 12
- **Monus (truncated subtraction)**: `uv run main 5 - 2` → Church numeral for 3

Church numeral encoding: `n = λf.λx.f(f(...f(x)...))` (n applications of f)

## Lambda Calculus Syntax

The interpreter supports the following syntax:

- **Variables**: `x`, `y`, `foo`, `bar123` (letter followed by alphanumerics)
- **Lambda abstraction**: `\x body` (represents λx.body)
- **Application**: `f x` (function application, left-associative)
- **Parentheses**: `(expr)` for grouping

### Examples (with β-reduction)

```
x                  → x                    # No reduction needed
\x x               → (\x x)               # Identity function (irreducible)
(\x x) y           → y                    # Identity applied: reduces to y
\x \y x            → (\x (\y x))          # Constant function (irreducible)
f x y              → ((f x) y)            # Application (irreducible without definition)
(\x x)(\y y)       → (\y y)               # Identity applied to identity
\f \x f (f x)      → (\f (\x (f (f x)))) # Church numeral 2 (irreducible)
```

## Testing

The project includes comprehensive test coverage with **58 test cases** organized into categories:

### Parser Tests (31 tests)

- **Empty Input** - Empty files, blank lines
- **Simple Variables** - Single variables, alphanumeric identifiers
- **Lambda Abstractions** - Identity, constant, nested abstractions
- **Applications** - Simple, chained, left-associative applications
- **Complex Expressions** - Church numerals, nested combinations
- **Parentheses** - Grouping, nested parentheses
- **Mixed Valid** - Expressions with blank lines
- **Invalid Expressions** - Missing variables, unclosed parens, unexpected chars
- **Edge Cases** - Whitespace handling, deeply nested expressions

### Interpreter Tests (27 tests)

- **Beta-Reduction** - Basic β-reduction functionality
- **Alpha-Conversion** - Variable capture avoidance
- **Normal Order Strategy** - Leftmost-outermost evaluation
- **Reduction Limit** - Step limit for non-terminating expressions
- **Assignment Examples** - All positive examples from assignment specification
- **Church Numerals** - Encoding, addition, multiplication, subtraction
- **Error Handling** - Syntax errors and invalid inputs

### Test Fixtures

The `tests/fixtures/` directory contains **18 test files**:

**Parser fixtures (from Assignment 1):**
- `empty.txt` - Empty file
- `blank_lines.txt` - Only whitespace
- `simple_variables.txt` - Basic variable names
- `lambda_abstractions.txt` - Various lambda abstractions
- `applications.txt` - Function applications
- `complex_expressions.txt` - Advanced expressions
- `parenthesized.txt` - Parenthesized expressions
- `mixed_valid.txt` - Valid with blank lines

**Interpreter fixtures (Assignment 2):**
- `beta_simple.txt` - Simple β-reductions
- `beta_reduction.txt` - Complex β-reductions
- `alpha_conversion.txt` - Variable capture cases
- `normal_order.txt` - Normal order evaluation test
- `omega.txt` - Non-terminating omega combinator

**Invalid inputs:**
- `invalid_missing_var.txt` - Lambda without variable
- `invalid_missing_body.txt` - Lambda without body
- `invalid_unclosed_paren.txt` - Unclosed parenthesis
- `invalid_unexpected_char.txt` - Invalid character (+)
- `invalid_number_start.txt` - Identifier starting with number

## Project Philosophy

This project demonstrates a hybrid approach:

- **OCaml** implements the core lambda calculus interpreter (lexer, parser, AST, reducer, renderer)
- **Python + pytest** provides comprehensive testing infrastructure
- **uv** unifies the developer experience with consistent commands
- **ruff** ensures Python code quality

This separation of concerns allows:
- Focus on interpreter logic in OCaml without test boilerplate
- Flexible, expressive tests in Python
- Easy CI/CD integration
- Simple onboarding for students familiar with Python

## Development Workflow

### Make Changes to OCaml Code

1. Edit `src/main.ml`
2. Format: `uv run format`
3. Build: `uv run build`
4. Test: `uv run test`

### Add New Tests

1. Add fixture file to `tests/fixtures/`
2. Add test case to `tests/test_lambda_parser.py`
3. Run tests: `uv run test`

### Direct OCaml Commands

If you prefer to use OCaml tools directly:

```bash
cd src
eval $(opam env)

# Build
dune build

# Run
dune exec main -- ../tests/fixtures/simple_variables.txt

# Format
dune build @fmt --auto-promote
```

## Troubleshooting

### `opam: command not found`

Install opam: `sudo apt-get install -y opam`

### `dune: command not found`

Source opam environment: `eval $(opam env)`

### Tests fail with "FileNotFoundError: dune"

The tests need the opam environment. Run tests via `uv run test` which handles this automatically.

### `uv: command not found`

Install uv: `curl -LsSf https://astral.sh/uv/install.sh | sh`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

Created for the Concepts of Programming Languages course at Leiden University.

## Resources

- [OCaml Manual](https://ocaml.org/manual/)
- [Dune Documentation](https://dune.build/)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Lambda Calculus (Wikipedia)](https://en.wikipedia.org/wiki/Lambda_calculus)
