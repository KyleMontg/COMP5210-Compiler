import argparse
import sys
from pathlib import Path
from src import *
from dataclasses import is_dataclass, asdict

def create_arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Tokenizes a C file')
    parser.add_argument(
        '-l',
        required=False,
        action='store_true',
        help='Prints Tokenized input to console',
    )
    parser.add_argument(
        '-a',
        required=False,
        action='store_true',
        help='Prints Abstract Syntax Tree to console',
    )
    parser.add_argument(
        '-t',
        required=False,
        action='store_true',
        help='Prints Token Table to console',
    )
    parser.add_argument(
        '-o',
        '--output',
        required=False,
        type=Path,
        help='Specify path to output file. Defaults to ./output.txt',
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Path to input file',
    )
    return parser

def ast_to_json(ast):
    if ast is None:
        return None
    if is_dataclass(ast):
        return {key: ast_to_json(value) for key, value in asdict(ast).items()}
    return ast

def run_compiler(input_path: Path, output_path: Path, print_outputs: bool) -> None:

    try:
        source = input_path.read_text()
    except FileNotFoundError:
        print(f'Input File Not Found: {input_path}')
        sys.exit(1)

    try:
        tokenizer = Tokenizer(source)
        token_list = tokenizer.tokenize()
    except LexerError as err:
        print(f'Lexer error: {err}')
        sys.exit(1)

    if print_outputs[0]:
        print('Token List: \n\n')
        for token in token_list:
            print(token)
        print('\n\n')

    try:
        parser = Parser(token_list)
        ast = parser.parse()
    except ParserError as err:
        print(f'Parser error: {err}')
        sys.exit(1)

    if print_outputs[1]:
        print(f'AST:\n\n{ast_to_json(ast)}\n\n')

    try:
        sym_table = SymbolTable()
        sym_table.build_symbol_table(ast)
    except SymbolTableError as err:
        print(f'Symbol Table error: {err}')
        sys.exit(1)


    if print_outputs[2]:
        print(f'Symbol Table\n\n{sym_table.dump()}\n\n')

    try:
        with open(output_path, 'w') as file:
            for token in token_list:
                file.write(f"{token}\n")
    except OSError as err:
        print(err)
        sys.exit(1)






if __name__ == '__main__':
    parser = create_arguments()
    args = parser.parse_args()

    print_outputs = [args.l, args.a, args.t]
    output_path = (Path.cwd() / args.output) if args.output else (Path.cwd() / 'output.txt')
    input_path = Path.cwd() / args.input

    run_compiler(input_path, output_path, print_outputs)