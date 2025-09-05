from pathlib import Path
import sys

src_file = str(Path(Path.cwd(),'src'))
sys.path.append(src_file)

#for x in enumerate(sys.path):
#    print(x)
import lexer
with open(Path('./test/test_code/test1.txt')) as f:
    a = lexer.Tokenizer(f)
    tokens = a.tokenize()
    for x in tokens:
        print(x)
