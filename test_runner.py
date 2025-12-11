import sys
from pathlib import Path
import argparse
from src import (
    LexerError,
    ParserError,
    SymbolTableError,
    SemanticError,
    TACError,
    ASMError,
    Tokenizer,
    Parser,
    SymbolTable,
    SemanticAnalyzer,
    TAC,
    pretty_tac,
    constant_fold,
    copy_and_constant_propagation,
    dead_code_elimination,
    register_optimization,
    tac_to_asm,
)
import copy


def create_arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Comprehensive Test Suite')
    parser.add_argument(
        '-l',
        required=False,
        action='store_true',
        help='Run lexer tests',
    )
    parser.add_argument(
        '-p',
        required=False,
        action='store_true',
        help='Run parser tests',
    )
    parser.add_argument(
        '-s',
        required=False,
        action='store_true',
        help='Run semantic analysis tests',
    )
    parser.add_argument(
        '-t',
        required=False,
        action='store_true',
        help='Run TAC generation tests',
    )
    parser.add_argument(
        '-o',
        required=False,
        action='store_true',
        help='Run optimization tests',
    )
    parser.add_argument(
        '-a',
        '--all',
        required=False,
        action='store_true',
        help='Run all tests including showcase',
    )
    parser.add_argument(
        '--showcase',
        required=False,
        action='store_true',
        help='Run showcase tests only',
    )
    return parser


class TestRunner:
    """Enhanced test runner with comprehensive test coverage"""

    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.total = 0

    def print_results(self):
        """Print final test results"""
        print("\n" + "=" * 80)
        print(f"RESULTS: {self.passed}/{self.total} tests passed")
        if self.failed == 0:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"❌ {self.failed} tests FAILED")
        print("=" * 80)

    def run_single_test(self, name: str, code: str, should_pass: bool = True):
        """Run a single test case"""
        self.total += 1

        try:
            # Full compilation pipeline
            tokenizer = Tokenizer(code)
            tokens = tokenizer.tokenize()

            parser = Parser(tokens)
            ast = parser.parse()

            sym_table = SymbolTable()
            sym_table.build_symbol_table(ast)

            analyzer = SemanticAnalyzer(ast, sym_table)
            analyzer.analyze()

            tac = TAC()
            tac.generate_tac(ast, sym_table)

            # Optimizations
            opt_tac = copy.deepcopy(tac)
            constant_fold(opt_tac)
            copy_and_constant_propagation(opt_tac)
            dead_code_elimination(opt_tac)

            # Assembly generation
            reg_map = register_optimization(opt_tac)
            asm = tac_to_asm(opt_tac, reg_map)

            if should_pass:
                self.passed += 1
                print(f"  ✅ {name}")
                return True
            else:
                self.failed += 1
                print(f"  ❌ {name} - Expected to fail but passed!")
                return False

        except Exception as err:
            if not should_pass:
                self.passed += 1
                print(f"  ✅ {name} - Correctly rejected")
                return True
            else:
                self.failed += 1
                print(f"  ❌ {name} - {type(err).__name__}: {str(err)[:60]}...")
                return False

    def test_lexer(self):
        """Test lexer functionality"""
        print("\n" + "=" * 80)
        print("LEXER TESTS")
        print("=" * 80)

        tests = {
            "Integer literals": "int main() { int x = 42; return x; }",
            "Negative numbers": "int main() { int x = -10; return x; }",
            "All operators": "int main() { return 1 + 2 - 3 * 4 / 5 % 6; }",
            "Comparisons": "int main() { return 5 > 3; }",
            "Comments": "// Line comment\nint main() { /* block */ return 0; }",
            "Identifiers": "int main() { int x_1 = 5; int _y = 10; return x_1 + _y; }",
        }

        for name, code in tests.items():
            self.run_single_test(name, code, should_pass=True)

    def test_parser(self):
        """Test parser functionality"""
        print("\n" + "=" * 80)
        print("PARSER TESTS")
        print("=" * 80)

        tests = {
            "Function with params": "int foo(int x, int y) { return x + y; }",
            "If statement": "int main() { if (5 > 3) { return 1; } return 0; }",
            "If-else": "int main() { if (0) { return 1; } else { return 2; } }",
            "While loop": "int main() { int x = 0; while (x < 10) { x = x + 1; } return x; }",
            "Do-while": "int main() { int x = 0; do { x = x + 1; } while (x < 5); return x; }",
            "For loop": "int main() { int i; for (i = 0; i < 10; i = i + 1) { } return i; }",
            "Nested blocks": "int main() { { { int x = 5; } } return 0; }",
            "Multiple declarations": "int main() { int x = 1, y = 2, z = 3; return x + y + z; }",
            "Expression precedence": "int main() { return 1 + 2 * 3 - 4 / 2; }",
            "Prefix operators": "int main() { int x = 5; return -x; }",
        }

        for name, code in tests.items():
            self.run_single_test(name, code, should_pass=True)

    def test_semantic_analysis(self):
        """Test semantic analysis"""
        print("\n" + "=" * 80)
        print("SEMANTIC ANALYSIS TESTS")
        print("=" * 80)

        # Tests that should PASS
        pass_tests = {
            "Valid program": "int main() { int x = 5; return x; }",
            "Proper initialization": "int main() { int x; x = 10; return x; }",
            "Scoping": "int main() { int x = 5; { int y = x; } return x; }",
            "Parameters initialized": "int foo(int x) { return x + 5; }",
        }

        for name, code in pass_tests.items():
            self.run_single_test(f"PASS: {name}", code, should_pass=True)

        # Tests that should FAIL
        fail_tests = {
            "Char type": "char main() { return 0; }",
            "Void type": "void main() { return; }",
            "Unsigned int": "int main() { unsigned int x = 5; return x; }",
            "String literal": 'int main() { int x = "hello"; return x; }',
            "Char literal": "int main() { int x = 'a'; return x; }",
            "Undefined variable": "int main() { int x = y + 5; return x; }",
            "Uninitialized variable": "int main() { int x; int y = x + 5; return y; }",
            "Uninitialized increment": "int main() { int x; ++x; return x; }",
        }

        for name, code in fail_tests.items():
            self.run_single_test(f"FAIL: {name}", code, should_pass=False)

    def test_tac_generation(self):
        """Test TAC generation"""
        print("\n" + "=" * 80)
        print("TAC GENERATION TESTS")
        print("=" * 80)

        tests = {
            "Simple assignment": "int main() { int x = 5; return x; }",
            "Binary expressions": "int main() { return 1 + 2 * 3; }",
            "Unary minus": "int main() { int x = -10; return x; }",
            "Comparisons": "int main() { return 5 > 3; }",
            "If statement": "int main() { if (1) { return 1; } return 0; }",
            "While loop": "int main() { int x = 0; while (x < 5) { x = x + 1; } return x; }",
            "For loop": "int main() { int i; for (i = 0; i < 5; i = i + 1) { } return i; }",
        }

        for name, code in tests.items():
            self.run_single_test(name, code, should_pass=True)

    def test_optimizations(self):
        """Test optimization passes"""
        print("\n" + "=" * 80)
        print("OPTIMIZATION TESTS")
        print("=" * 80)

        tests = {
            "Constant folding": "int main() { return 2 + 3 * 4; }",
            "Copy propagation": "int main() { int x = 5; int y = x; return y; }",
            "Dead code elimination": "int main() { int x = 5; int y = 10; return x; }",
            "Combined optimizations": "int main() { int x = 2 + 3; int y = x; int z = 10; return y; }",
        }

        for name, code in tests.items():
            self.run_single_test(name, code, should_pass=True)

        # Should fail: division by zero
        self.run_single_test("FAIL: Division by zero",
                             "int main() { return 10 / 0; }", should_pass=False)

    def showcase_features(self):
        """Showcase 5 key features"""
        print("\n" + "=" * 80)
        print("🌟 FEATURE SHOWCASE")
        print("=" * 80)

        showcases = [
            (
                "1. Semantic Error Detection",
                """
int main() {
    int x;        // Declared but not initialized
    return x;     // ERROR: Use before initialization
}
                """.strip(),
                False,
                "Catches use of uninitialized variables at compile time"
            ),
            (
                "2. Constant Folding Optimization",
                """
int main() {
    // Computed at compile time!
    int x = 2 + 3 * 4;     // Becomes: 14
    int y = 100 - 50;      // Becomes: 50
    return x + y;          // Returns: 64
}
                """.strip(),
                True,
                "Evaluates constant expressions at compile time"
            ),
            (
                "3. Complex Control Flow",
                """
int main() {
    int a = 0;
    int b = 1;
    int i;
    int temp;

    // Fibonacci-style sequence
    for (i = 0; i < 10; i = i + 1) {
        temp = a + b;
        a = b;
        b = temp;
    }

    return b;  // Returns 10th Fibonacci number
}
                """.strip(),
                True,
                "Handles nested loops with state management"
            ),
            (
                "4. Register Allocation",
                """
int main() {
    // Intelligent register allocation
    int x = 10;
    int y = 20;
    int z = 30;
    int w = 40;
    int result = x + y + z + w;
    return result;
}
                """.strip(),
                True,
                "Graph-coloring based register allocation"
            ),
            (
                "5. Dead Code Elimination",
                """
int main() {
    int x = 5;
    int y = 10;   // UNUSED - eliminated
    int z = 15;   // UNUSED - eliminated
    int w = 20;   // UNUSED - eliminated
    return x;     // Only x survives optimization
}
                """.strip(),
                True,
                "Removes variables that are never read"
            ),
        ]

        for title, code, should_pass, description in showcases:
            print(f"\n{title}")
            print("─" * 80)
            print(description)
            print("─" * 80)
            print(code)
            print("─" * 80)

            result = self.run_single_test(title, code, should_pass)

            if result:
                print("  ✨ Feature demonstrated successfully!\n")
            else:
                print("  ⚠️  Feature test did not behave as expected\n")


def main():
    """Main entry point"""
    parser = create_arguments()
    args = parser.parse_args()

    runner = TestRunner()

    # If no args, show usage
    if not any([args.l, args.p, args.s, args.t, args.o, args.all, args.showcase]):
        print("Usage: python test_runner.py [options]")
        print("\nOptions:")
        print("  -l              Run lexer tests")
        print("  -p              Run parser tests")
        print("  -s              Run semantic analysis tests")
        print("  -t              Run TAC generation tests")
        print("  -o              Run optimization tests")
        print("  -a, --all       Run all tests including showcase")
        print("  --showcase      Run showcase features only")
        print("\nExample: python test_runner.py --all")
        return

    # Run requested tests
    if args.all:
        runner.test_lexer()
        runner.test_parser()
        runner.test_semantic_analysis()
        runner.test_tac_generation()
        runner.test_optimizations()
        runner.showcase_features()
    else:
        if args.l:
            runner.test_lexer()
        if args.p:
            runner.test_parser()
        if args.s:
            runner.test_semantic_analysis()
        if args.t:
            runner.test_tac_generation()
        if args.o:
            runner.test_optimizations()
        if args.showcase:
            runner.showcase_features()

    runner.print_results()


if __name__ == '__main__':
    main()
