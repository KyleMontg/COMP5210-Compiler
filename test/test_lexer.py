from pathlib import Path
import sys
import glob
src_file = str(Path(Path.cwd(),'src'))
sys.path.append(src_file)
from lexer import Tokenizer, Token
from tokens import *

def test_keywords():
    tok = Tokenizer("")
    for case, token_type in KEYWORDS.items():
        tok.set_new_file(case)
        assert(tok.tokenize() == [Token(token_type, case)])


def test_symbols():
    tok = Tokenizer("")
    for case, token_type in SYMBOLS.items():
        tok.set_new_file(case)
        assert(tok.tokenize() == [Token(token_type, case)])

def test_comments():
    tok = Tokenizer('//')
    assert(tok.tokenize() == [])

    tok.set_new_file("/*")
    assert(tok.tokenize() == [])

def test_other_tokens():
    tok = Tokenizer("cokezero")
    assert(tok.tokenize() == [Token("IDENTIFIER", "cokezero")])

    tok.set_new_file("123")
    assert(tok.tokenize() == [Token("NUMBER", "123")])
    tok.set_new_file("'AAAB' x")
    assert(tok.tokenize() == [Token("CHAR_LITERAL", "AAAB"), Token("IDENTIFIER", "x")])
    tok.set_new_file('"AAAB" x')
    assert(tok.tokenize() == [Token("STRING_LITERAL", "AAAB"), Token("IDENTIFIER", "x")])

def test_edge_cases():
    tok = Tokenizer("")
    assert(tok.tokenize() == [])

def test_code():
    test_path = Path(src_file, '/test/test_code')
    for files in glob.iglob(str(Path(test_path, '*.c'))):
        with open(files) as f:
            tok = Tokenizer(f.read())
            token_list= tok.tokenize()


