#TODO Implement args, and run test if needed
import argparse


def create_arguments():
    parser = argparse.ArgumentParser(
    description = '' #TODO
    )

    # List tokens
    parser.add_argument(
        '-l',
        "--list",
        required=False,
        help = 'Prints parsed tokens to the console'
    )

    # File location
    parser.add_argument(
        '-f',
        "--file",
        required=False,
        help = 'Location of the file to be tokenized'
    )

    # Run Tests
    parser.add_argument(
        '-t',
        "--test",
        required=False,
        help = 'Runs the default tests for tokenizer'
    )

    # Output file location
    parser.add_argument(
        '-o',
        "--output",
        required=False,
        help = 'specifies where output file is generate. Defaults to local folder.'
    )
    return parser

if __name__ == '__main__':
    parser = create_arguments()
    args = parser.parse_args()
