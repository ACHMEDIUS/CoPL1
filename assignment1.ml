(* Lambda-calculus lexical analyzer and parser. *)

exception Syntax_error of string

type expr =
  | Var of string
  | Abs of string * expr
  | App of expr * expr

type token =
  | Tok_lambda
  | Tok_lparen
  | Tok_rparen
  | Tok_identifier of string
  | Tok_eof

let usage_msg = "Usage: dune exec assignment1 -- <input-file>"

let is_letter c =
  ('a' <= c && c <= 'z') || ('A' <= c && c <= 'Z')

let is_digit c =
  '0' <= c && c <= '9'

let is_alphanum c = is_letter c || is_digit c

let unexpected_character c =
  raise (Syntax_error (Printf.sprintf "Unexpected character: %c" c))

(* Read the entire contents of a file into a string. *)
let read_file filename =
  let channel = open_in filename in
  Fun.protect
    ~finally:(fun () -> close_in_noerr channel)
    (fun () ->
      let len = in_channel_length channel in
      really_input_string channel len)

let tokenize source : token list =
  let len = String.length source in
  let rec lex idx acc =
    if idx >= len then
      List.rev (Tok_eof :: acc)
    else
      match source.[idx] with
      | ' ' | '\t' | '\r' -> lex (idx + 1) acc
      | '\n' -> lex (idx + 1) acc
      | '\\' -> lex (idx + 1) (Tok_lambda :: acc)
      | '(' -> lex (idx + 1) (Tok_lparen :: acc)
      | ')' -> lex (idx + 1) (Tok_rparen :: acc)
      | c when is_letter c ->
          let stop =
            let rec advance j =
              if j < len && is_alphanum source.[j] then
                advance (j + 1)
              else
                j
            in
            advance (idx + 1)
          in
          let name = String.sub source idx (stop - idx) in
          lex stop (Tok_identifier name :: acc)
      | c -> unexpected_character c
  in
  lex 0 []

let expect_identifier tokens =
  match tokens with
  | Tok_identifier name :: rest -> (name, rest)
  | [] -> raise (Syntax_error "Missing variable after lambda")
  | Tok_eof :: _ -> raise (Syntax_error "Missing variable after lambda")
  | Tok_lparen :: _ -> raise (Syntax_error "Missing variable after lambda")
  | Tok_rparen :: _ -> raise (Syntax_error "Missing variable after lambda")
  | Tok_lambda :: _ -> raise (Syntax_error "Missing variable after lambda")

let rec parse_expression tokens =
  match tokens with
  | Tok_lambda :: _ -> parse_abstraction tokens
  | _ -> parse_application tokens

and parse_abstraction tokens =
  match tokens with
  | Tok_lambda :: rest ->
      let var, rest_tokens = expect_identifier rest in
      let rest_tokens =
        match rest_tokens with
        | Tok_eof :: _ -> raise (Syntax_error "Missing expression after lambda abstraction")
        | _ -> rest_tokens
      in
      let body, remaining = parse_expression rest_tokens in
      (Abs (var, body), remaining)
  | _ -> assert false

and parse_application tokens =
  let lhs, rest = parse_atom tokens in
  parse_application_tail lhs rest

and parse_application_tail lhs tokens =
  match tokens with
  | Tok_identifier _ :: _
  | Tok_lparen :: _
  | Tok_lambda :: _ ->
      let rhs, rest = parse_atom tokens in
      parse_application_tail (App (lhs, rhs)) rest
  | _ -> (lhs, tokens)

and parse_atom tokens =
  match tokens with
  | Tok_identifier name :: rest -> (Var name, rest)
  | Tok_lparen :: rest ->
      let expr, rest_after_expr = parse_expression rest in
      (match rest_after_expr with
       | Tok_rparen :: rest_final -> (expr, rest_final)
       | Tok_eof :: _ -> raise (Syntax_error "Missing closing parenthesis")
       | _ -> raise (Syntax_error "Missing closing parenthesis"))
  | Tok_lambda :: _ -> parse_abstraction tokens
  | Tok_rparen :: _ -> raise (Syntax_error "Missing expression after opening parenthesis")
  | Tok_eof :: _ -> raise (Syntax_error "Unexpected end of input")
  | [] -> raise (Syntax_error "Unexpected end of input")

let parse tokens : expr =
  let expr, rest = parse_expression tokens in
  match rest with
  | [Tok_eof] -> expr
  | Tok_eof :: _ -> raise (Syntax_error "Input string not fully parsed")
  | _ -> raise (Syntax_error "Input string not fully parsed")

let rec render expr =
  match expr with
  | Var name -> name
  | App (lhs, rhs) ->
      let left = render lhs in
      let right = render rhs in
      Printf.sprintf "(%s %s)" left right
  | Abs (name, body) ->
      let body_str = render body in
      Printf.sprintf "(\\%s %s)" name body_str

let process_expression line =
  let tokens = tokenize line in
  let ast = parse tokens in
  render ast

let is_blank_line line =
  let rec loop idx =
    if idx >= String.length line then
      true
    else
      match line.[idx] with
      | ' ' | '\t' | '\r' -> loop (idx + 1)
      | _ -> false
  in
  loop 0

let process_file filename =
  let source = read_file filename in
  let expressions = String.split_on_char '\n' source in
  expressions
  |> List.filter (fun line -> not (is_blank_line line))
  |> List.map process_expression

let () =
  if Array.length Sys.argv <> 2 then begin
    prerr_endline usage_msg;
    raise (Invalid_argument usage_msg)
  end;
  let input_file = Sys.argv.(1) in
  let outputs = process_file input_file in
  List.iter print_endline outputs
