from tokens import *

# TODO Comment

HEX_DIGITS = {
    '0',
    '1',
    '2',
    '3',
    '4',
    '5',
    '6',
    '7',
    '8',
    '9',
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
}
class Token:
    def __init__(self, token_type: str, value:str, line_num:int = -1, char_num: int = -1):
        self.type = token_type
        self.value = value
        self.line_num = line_num
        self.char_num = char_num

    def __repr__(self) -> str:
        if(self.line_num > -1):
            return f"({self.type},'{self.value}', Line: {self.line_num + 1} Char: {self.char_num})"
        return  f"({self.type},'{self.value}')"

    def __eq__(self, other) -> bool:
        return self.value == other.value and self.type == other.type

class Tokenizer:
    def __init__(self):
        self.token_list = []
        self.SYMBOL_PREFIXES = set()
        self.in_mlc = False
        for symbol in SYMBOLS:
            for index, _ in enumerate(symbol):
                self.SYMBOL_PREFIXES.add(symbol[:index+1])

    def _test_whitespace(self, char):
        return True if(char == ' ') else False

    def _test_slc(self, poss_slc):
        return poss_slc == '//'


# can_continue, is_final, token
    def _is_identifier(self, poss_ident: str) -> tuple[bool, bool, Token|None]: # combinations: True, False | False, False | True, True
        if(poss_ident[0].isdigit):
            return(False, False, None)
        for char in poss_ident:
            if(not (char.isalnum() or char == '_')):
                return (False, False, None)
        return (True, True, Token(IDENTIFIER, poss_ident))

    def _is_symbol(self, poss_sym: str) -> tuple[bool, bool, Token|None]:
        if(poss_sym == "" or len(poss_sym) > 3):
            return (False, False, None)
        can_continue = poss_sym in self.SYMBOL_PREFIXES
        is_final = False
        symbol_token = None
        if(full_symbol := SYMBOLS.get(poss_sym)):
            is_final = True
            symbol_token = Token(full_symbol, poss_sym)
        return (can_continue, is_final, symbol_token)

    def _is_integer(self, poss_dec):
        for char in poss_dec:
            if(not char.isdigit()):
                return (False, False, None)
        return (True, True, Token('placeholder integer', poss_dec))#TODO replace placeholder

    def _is_octal(self, poss_octal: str):
        if(poss_octal[0] != '0'):
            return (False, False, None)
        for char in poss_octal:
            if(not char.isdigit() or char == '9'):
                return (False, False, None)
        return (True, True, Token('placeholder octal', poss_octal))#TODO replace placeholder

    def _is_hex(self, poss_hex: str):
        if(poss_hex[0] != '0'):
            return (False, False, None)
        if(len(poss_hex) < 3):
            return (True, False, None)
        if(poss_hex[1].lower() != 'x'):
            return (False, False, None)
        for char in poss_hex[2:]:
            if(char.lower() not in HEX_DIGITS):
                return(False, False, None)
        return (False, True, Token('placeholder hex', poss_hex))#TODO replace placeholder


    def _is_decimal_float(self, poss_d_float: str):
        # check if first half is number
        # if i reach dec
        # check second
        for char in poss_d_float:
            if(char.isdigit()):
                continue
            elif(char == '.'):
                break
            else:
                return (False, False, None)
        after_digit = poss_d_float.split('.', 1)[1]
        if(len(after_digit) == 0):
            return (True, False, None)
        for char in after_digit:
            if(not char.isdigit()):
                return (False, False, None)
        return (True, True, Token('placeholder decimal float', poss_d_float))#TODO replace placeholder

    def _is_hex_float(self, poss_hex_float): #TODO Incomplete
        if(poss_hex_float[0] != '0'):
            return (False, False, None)
        if(len(poss_hex_float) < 3):
            return (True, False, None)
        if(poss_hex_float[1].lower() != 'x'):
            return (False, False, None)
        for char in poss_hex_float:
            if(char.isdigit()):
                continue
            elif(char == '.'):
                break
            else:
                return (False, False, None)
        after_digit = poss_d_float.split('.', 1)[1]
        if(len(after_digit) == 0):
            return (True, False, None)
        for char in after_digit:
            if(not char.isdigit()):
                return (False, False, None)
        return (True, True, Token('placeholder decimal float', poss_d_float))#TODO replace placeholder

    def _is_string_literal(self, poss_str):
        if(poss_str[0] != '"'):
            return (False, False, None)
        if(len(poss_str) > 1 and poss_str[-1] == '"'):
            return (False, True, Token(STRING_LITERAL, poss_str[1:-1]))
        return (True, False, None)

    def _is_char_literal(self, poss_char):
        if(poss_char[0] != "'"):
            return (False, False, None)
        if(len(poss_char) > 1 and poss_char[-1] == "'"):
            return (False, True, Token(CHAR_LITERAL, poss_char[1:-1]))
        return (True, False, None)

    def _test_mlc(self, line):
        mlc_start = line.find('*/')
        mlc_end = line.find('/*', mlc_start + 2)
        if(self.in_mlc):
            mlc_end = line.find('/*')
            if(mlc_end != -1):
                line_end = line[mlc_end + 2:]
                line = (' ' * (mlc_end + 2)) + line_end
                self.in_mlc = False
        if(mlc_start != -1):
            line_start = line[:mlc_start]
            if(mlc_end != -1):
                line_end = line[mlc_end + 2:]
                line = line_start + (' ' * (mlc_end + 2 - mlc_start)) + line_end
            else:
                line = line_start
                self.in_mlc = True
        return (line)


    def _add_token(self, token: Token):
        if(not token):
            raise Exception("empty token")
        self.token_list.append(token)

    def _tokenize_line(self, line: str):
        raw_line = line
        line = self._test_mlc(line)
        while(raw_line != line):
            raw_line = line
            line = self._test_mlc(line)
        if(self.in_mlc):
            return
        start_index = 0
        curr_index = 0
        # Order of functions_list is first function least token presedence
        functions_list = [
            self._is_string_literal,
            self._is_char_literal,
            self._is_identifier,
            self._is_symbol
            ]
        curr_functions = functions_list.copy()
        keep_functions = []
        last_token = None
        while(len(line) > curr_index):
            curr_token = None
            if(self._test_whitespace(line[curr_index])):
                if(last_token):
                    self._add_token(last_token)
                    last_token = None
                curr_functions = functions_list.copy()
                curr_index += 1
                start_index = curr_index
                continue
            if(self._test_slc):
                curr_index = len(line)
                continue
            for builder in curr_functions:
                results = builder(line[start_index:curr_index + 1])
                if(results[0]):
                    keep_functions.append(builder)
                if(results[1]):
                    curr_token = results[2]
            curr_functions = keep_functions.copy()
            keep_functions = []
            if(not curr_token):
                self._add_token(last_token)
                last_token = None
                curr_functions = functions_list.copy()
                start_index = curr_index
            else:
                last_token = curr_token
                curr_index += 1
        #TODO add add last token?
        self._add_token(Token(EOL, None))
