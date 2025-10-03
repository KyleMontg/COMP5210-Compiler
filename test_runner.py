import glob
from pathlib import Path
from src import *
import argparse


def create_arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Test Compiler')
    parser.add_argument(
        '-l',
        required=False,
        action='store_true',
        help='runs tests on lexer.py',
    )
    parser.add_argument(
        '-a',
        required=False,
        action='store_true',
        help='runs test on parser.py',
    )
    parser.add_argument(
        '-t',
        required=False,
        action='store_true',
        help='runs tests on symbol_table.py',
    )
    return parser

class TestHandler():
    def __init__(self):
        pass

    def test_lexer(self):
        for filename in Path('test/test_code/').glob('*.c'):
            source = filename.read_text()
            test_name = filename.stem
            try:
                tokenizer = Tokenizer(source)
                tokenizer.tokenize()
            except LexerError as err:
                print(f'\nLexer Failed at {str(test_name)}:\n')
                print(err)
                continue
            print(f'{test_name} sucessfully tokenized!')
        print('\nDone Testing Lexer')

    def test_parser(self):
        for filename in Path('test/test_code/').glob('*.c'):
            source = filename.read_text()
            test_name = filename.stem
            try:
                tokenizer = Tokenizer(source)
                toks = tokenizer.tokenize()
                parser = Parser(toks)
                parser.parse()
            except LexerError as err:
                print(f'\nLexer Failed at {test_name}:\n')
                print(err)
                continue
            except ParserError as err:
                print(f'\nParser Failed at {test_name}:\n')
                print(err)
                continue
            print(f'{test_name} sucessfully parsed!')
        print('\nDone Testing Parser')

    def test_symbol_table(self):
        for filename in Path('test/test_code/').glob('*.c'):
            source = filename.read_text()
            test_name = filename.stem
            try:
                tokenizer = Tokenizer(source)
                toks = tokenizer.tokenize()
                parser = Parser(toks)
                ast_toks = parser.parse()
                sym_tab = SymbolTable()
                sym_tab.build_symbol_table(ast_toks)

            except LexerError as err:
                print(f'\nLexer Failed at {test_name}:\n')
                print(err)
                continue
            except ParserError as err:
                print(f'\nParser Failed at {test_name}:\n')
                print(err)
                continue
            except SymbolTableError as err:
                print(f'\nSymbolTable Failed at {test_name}:\n')
                print(err)
                continue
            print(f'{test_name} sucessfully parsed!')
        print('\nDone Testing Parser')


if __name__ == '__main__':
    parser = create_arguments()
    args = parser.parse_args()
    test_lexer, test_parser, test_ast = args.l, args.a, args.t
    tester = TestHandler()
    if(test_lexer):
        tester.test_lexer()
    if(test_parser):
        tester.test_parser()
    if(test_ast):
        tester.test_symbol_table()
