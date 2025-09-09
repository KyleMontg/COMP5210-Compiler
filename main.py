import sys
import argparse
from pathlib import Path
src_file = str(Path(Path.cwd(),'src'))
sys.path.append(src_file)
from lexer import Tokenizer

def create_arguments():
    parser = argparse.ArgumentParser(
    description = 'Tokenizes a c file'
    )
    # List tokens
    parser.add_argument(
        '-l',
        "--list",
        required=False,
        action = 'store_true',
        help = 'Prints parsed tokens to the console'
    )
    # Output file location
    parser.add_argument(
        '-o',
        "--output",
        required=False,
        type = Path,
        help = 'Specify path to output file. Defaults to ./output.txt'
    )
    # File location to be compiled
    parser.add_argument(
        "input",
        type = Path,
        help = 'Path to input file'
    )
    return parser

def run_tokenizer(input_path: Path, output_path: Path, print_bool: bool):
    token_list = []
    try:
        with open(input_path) as f:
            tok = Tokenizer(f.read())
            token_list = tok.tokenize()
            if(print_bool):
                for tokens in token_list:
                    print(tokens)
    except FileNotFoundError:
            print(f"Input File Not Found: {input_path}")
            sys.exit(1)


    try:
        with open(output_path, "w") as f:
            for tokens in token_list:
                f.write(str(tokens))
                f.write("\n")

    except Exception as e:
        print(e)
        sys.exit(1)

if __name__ == '__main__':
    parser = create_arguments()
    args = parser.parse_args()
    list_bool = args.list
    output_path = Path(Path.cwd(), args.output) if args.output else Path(Path.cwd(), "output.txt")
    input_path = Path(Path.cwd(), args.input)
    run_tokenizer(input_path, output_path, list_bool)