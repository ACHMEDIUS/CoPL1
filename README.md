# Lambda Calculus Parser

A lexer and parser for lambda calculus expressions, created for the CoPL (Concepts of Programming Languages) course at Leiden University.

## Project Structure

```
.
├── src/                     # OCaml source code
│   ├── main.ml              # Lambda calculus lexer, parser, and renderer
│   ├── dune                 # Build configuration
│   ├── dune-project         # Project metadata 
│   ├── main.opam            # Package dependencies
│   └── .ocamlformat         
├── tests/                   # Python test suite (31 tests)
│   ├── fixtures/            
│   └── test_lambda_parser.py 
├── scripts/                 # Python wrapper scripts
│   ├── build.py             # Build OCaml project
│   ├── format_code.py       # Format OCaml + Python code
│   ├── run_parser.py        # Run the parser
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

### 3. Run the Parser

```bash
# Using a test fixture
uv run main tests/fixtures/simple_variables.txt

# Using your own file
echo "\x x" > my_input.txt
uv run main my_input.txt
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
# Run the parser on a file
uv run main <input-file>

# Examples
uv run main tests/fixtures/simple_variables.txt
uv run main tests/fixtures/lambda_abstractions.txt
```

### Test

```bash
# Run all tests (31 test cases)
uv run test

# Run specific test class
uv run test tests/test_lambda_parser.py::TestEmptyInput -v

# Run with pytest options
uv run test -k "lambda" -v
```

### Format

```bash
# Format both OCaml and Python code
uv run format
```

This will:
- Format all OCaml code in `src/` using ocamlformat
- Format all Python code in `tests/` and `scripts/` using ruff

## Lambda Calculus Syntax

The parser supports the following syntax:

- **Variables**: `x`, `y`, `foo`, `bar123` (letter followed by alphanumerics)
- **Lambda abstraction**: `\x body` (represents λx.body)
- **Application**: `f x` (function application, left-associative)
- **Parentheses**: `(expr)` for grouping

### Examples

```
x                  → x
\x x               → (\x x)              # Identity function
\x \y x            → (\x (\y x))         # Constant function
f x y              → ((f x) y)           # Left-associative application
(\x x) y           → ((\x x) y)          # Apply identity to y
\f \x f (f x)      → (\f (\x (f (f x)))) # Church numeral 2
```

## Testing

The project includes comprehensive test coverage with **31 test cases** organized into categories:

### Test Categories

- **Empty Input** - Empty files, blank lines
- **Simple Variables** - Single variables, alphanumeric identifiers
- **Lambda Abstractions** - Identity, constant, nested abstractions
- **Applications** - Simple, chained, left-associative applications
- **Complex Expressions** - Church numerals, nested combinations
- **Parentheses** - Grouping, nested parentheses
- **Mixed Valid** - Expressions with blank lines
- **Invalid Expressions** - Missing variables, unclosed parens, unexpected chars
- **Edge Cases** - Whitespace handling, deeply nested expressions

### Test Fixtures

The `tests/fixtures/` directory contains **13 test files**:

**Valid inputs:**
- `empty.txt` - Empty file
- `blank_lines.txt` - Only whitespace
- `simple_variables.txt` - Basic variable names
- `lambda_abstractions.txt` - Various lambda abstractions
- `applications.txt` - Function applications
- `complex_expressions.txt` - Advanced expressions
- `parenthesized.txt` - Parenthesized expressions
- `mixed_valid.txt` - Valid with blank lines

**Invalid inputs:**
- `invalid_missing_var.txt` - Lambda without variable
- `invalid_missing_body.txt` - Lambda without body
- `invalid_unclosed_paren.txt` - Unclosed parenthesis
- `invalid_unexpected_char.txt` - Invalid character (+)
- `invalid_number_start.txt` - Identifier starting with number

## Project Philosophy

This project demonstrates a hybrid approach:

- **OCaml** implements the core lambda calculus parser (lexer, parser, AST, renderer)
- **Python + pytest** provides the testing infrastructure
- **uv** unifies the developer experience with consistent commands
- **ruff** ensures Python code quality

This separation of concerns allows:
- Focus on parsing logic in OCaml without test boilerplate
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
