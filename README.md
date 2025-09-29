# Assignment 1

- Group: 8
- Student: Behrad Farahani (s3323129)

## What works
- Program meets the following requirements:
  - Accepts a single command-line filename argument and reports misuse otherwise.
  - Reads printable ASCII expressions from the specified file.
  - Ignores blank lines and handles multiple expressions, one per line.
  - Tokenizes variable names, lambdas, and parentheses according to the grammar.
  - Parses expressions with correct precedence and left associativity.
  - Detects syntax errors (missing pieces, extra tokens, unmatched parentheses) and raises exceptions.
  - Produces a fully parenthesized λ-calculus expression that can be re-parsed to the same AST.

## How it works
- Each non-empty input line is tokenized into λ-calculus tokens, parsed via recursive descent (abstractions, applications, parentheses), and printed as a fully parenthesized expression that round-trips through the parser.
