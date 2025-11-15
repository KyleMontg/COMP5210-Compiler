import argparse
import sys
import importlib
from pathlib import Path
from src import *
import copy

def create_arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Tokenizes a C file')
    parser.add_argument(
        'input',
        type=Path,
        help='Path to input file',
    )
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
        '-w',
        '--write',
        required=False,
        type=Path,
        help='Specify path to output file. Defaults to ./output.txt',
    )
    parser.add_argument(
        '-o0',
        required=False,
        action='store_true',
        help='Three Address Code without optimizations',
    )
    parser.add_argument(
        '-o1',
        required=False,
        action='store_true',
        help='Three Address Code with constant folding pass',
    )

    return parser


def run_compiler(input_path: Path, output_path: Path, print_outputs: list) -> None:

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
        print('AST:\n')
        print(pretty_ast(ast))
        print('\n')

    try:
        sym_table = SymbolTable()
        sym_table.build_symbol_table(ast)
    except SymbolTableError as err:
        print(f'Symbol Table error: {err}')
        sys.exit(1)


    if print_outputs[2]:
        print(f'Symbol Table\n\n{sym_table.dump()}\n\n')


    try:
        tac = TAC()
        tac.generate_tac(ast, sym_table)
        cfg = build_cfg(tac)
    except TACError as err:
        print(f"Three Address Code error: {err}")
        sys.exit(1)
    '''
    try:
        pre_optimized = tac
        post_optimized = None
        while(True):
            post_optimized = constant_fold(copy.deepcopy(pre_optimized))
            post_optimized = copy_propagation(copy.deepcopy(post_optimized))
            post_optimized = dead_code_elimination(copy.deepcopy(post_optimized))
            print("\nPre OP")
            print(pretty_tac(pre_optimized))
            print("\nPost OP")
            print(pretty_tac(post_optimized))
            if(tac_equals(pre_optimized, post_optimized, include_meta=True)):
                break
            else:
                pre_optimized = post_optimized

    except TACError as err:
        print(f"Three Address Code error: {err}")
        sys.exit(1)
    '''

    if print_outputs[3]:
        print('Three Address Code without optimization: \n\n')
        print(pretty_tac(tac))
        print('\n\n')

    if print_outputs[4]:
        print(f'Three Address Code with Constant Folding: \n\n')
        print(pretty_tac(post_optimized))
        print('\n\n')
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

    print_outputs = [args.l, args.a, args.t, args.o0, args.o1]
    output_path = (Path.cwd() / args.write) if args.write else (Path.cwd() / 'output.txt')
    input_path = Path.cwd() / args.input

    run_compiler(input_path, output_path, print_outputs)
