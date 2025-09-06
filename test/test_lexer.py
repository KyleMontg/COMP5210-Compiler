from pathlib import Path
import sys

src_file = str(Path(Path.cwd(),'src'))
sys.path.append(src_file)

#for x in enumerate(sys.path):
#    print(x)
import lexer
with open(Path('./test/test_code/test1.c')) as f:
    a = lexer.Tokenizer(f)
    tokens = a.tokenize()
    for x in tokens:
        print(x)


def run_tests(dir_path: Path, print: bool):
    test_path = Path(dir_path, '/test/test_code')
    with open(test_path) as f:

