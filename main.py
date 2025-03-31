import sys
import os
from toks import *
from exceptions import *
from bcolors import *

#   Author         : Terence Feeser
#   Course and Year: BSCS 2A

#   Language Description:
#   The language generates valid arithmetic expressions involving add and multiply operations. The language
#   also supports parenthesis
# 
#   Language Grammar:
#   N = {E, E', T, T', F}
#   T = {+, *, (, ), 0, 1, 2, 3, 4, 5, 6, 7, 8, 9}
#   S = E
#   P = {
#       E -> T E'
#       E' -> + T E' | e
#       T -> F T'
#       T' -> * F T' | e
#       F -> (E) | int
#   }
# 
#   NOTE: int refers to a series of the terminals 0-9
#         e refers to the empty derivation, epsilon

#   The grammar described is for reference only, and the implementation details below might be slightly different.

#   Parser Details:
#   The parser implemented is an LL(1) parser. A helper function tokenize is implemented to simplify integers with multiple terminals
#   to a single token. It also transforms the other terminals into tokens. The tokens can be found in toks.py
#   
#   To implement the parser, we need to do a few things. We first compute the grammar's FIRSTS and FOLLOWS sets

#   FIRSTS(E) = {(, int}
#   FIRSTS(E') = {+, e}
#   FIRSTS(T) = {(, int}
#   FIRSTS(T') = {*, e}
#   FIRSTS(F) = {(, int}

#   FOLLOWS(E) = {), #EOS}
#   FOLLOWS(E') = {), #EOS}
#   FOLLOWS(T) = {+, ), #EOS}
#   FOLLOWS(T') = {+, ), #EOS}
#   FOLLOWS(F) = {+, *, ), #EOS}

#   We can now construct the parser table
#   
#   +----+--------------+-------------+-----------+---------+-----------+---------+
#   | _  |      +       |      *      |     (     |    )    |    int    |  #EOS   |
#   +----+--------------+-------------+-----------+---------+-----------+---------+
#   | E  |              |             | E -> T E' |         | E -> T E' |         |
#   | E' | E' -> + T E' |             |           | E' -> e |           | E' -> e |
#   | T  |              |             | T-> F T'  |         | T-> F T'  |         |
#   | T' | T'->         | T'-> * F T' |           | T'->    |           | T'->    |
#   | F  |              |             | F-> ( E ) |         | F -> int  |         |
#   +----+--------------+-------------+-----------+---------+-----------+---------+

#   Using this parsing table, we can now parse a tokenized input string and determine
#   whether the string is a valid string of our grammar

# Create parsing table as dicts for easy pattern matching
parsing_table = dict()
parsing_table["E"] = dict()
parsing_table["E'"] = dict()
parsing_table["T"] = dict()
parsing_table["T'"] = dict()
parsing_table["F"] = dict()

parsing_table["E"][LEFT_PAREN_TOK] = ["T", "E'"]
parsing_table["E"][INT_TOK] = ["T", "E'"]

parsing_table["E'"][ADD_TOK] = [ADD_TOK,"T", "E'"]
parsing_table["E'"][RIGHT_PAREN_TOK] = []
parsing_table["E'"][EOS_TOK] = []

parsing_table["T"][LEFT_PAREN_TOK] = ["F", "T'"]
parsing_table["T"][INT_TOK] = ["F", "T'"]

parsing_table["T'"][ADD_TOK] = []
parsing_table["T'"][MUL_TOK] = [MUL_TOK, "F", "T'"]
parsing_table["T'"][RIGHT_PAREN_TOK] = []
parsing_table["T'"][EOS_TOK] = []

parsing_table["F"][LEFT_PAREN_TOK] = [LEFT_PAREN_TOK, "E", RIGHT_PAREN_TOK]
parsing_table["F"][INT_TOK] = [INT_TOK]

# Rebuilds string from tokens and marks the location of the error using colors
def rebuild_and_mark_error(toks: list, pointer_to_error: int) -> None:
    result = f"{bcolors.OKCYAN}{bcolors.BOLD}\""

    for tok in toks:
        if toks[pointer_to_error] == tok:
            result += f"{bcolors.ENDC}{bcolors.FAIL}{bcolors.UNDERLINE}{tok.value}{bcolors.ENDC}"
        else:
            result += f"{bcolors.OKCYAN}{bcolors.BOLD}{tok.value}"

    result += f"{bcolors.OKCYAN}{bcolors.BOLD}\"{bcolors.ENDC}"
    return result

# Tokenize an input string
def tokenize(input_str: str) -> list:
    toks = []
    int_buffer = ""
    last_char_type = None

    for char in input_str:
        # Tokenize series of digits as a single int
        if char.isnumeric():
            int_buffer += char
            last_char_type = int
            continue
        # Push int token if we stopped reading digits and last char type is int
        elif last_char_type == int:
            toks.append(INT_TOK(int(int_buffer)))
            int_buffer = ""

        # Tokenize other chars
        if char == "+":
            toks.append(ADD_TOK())
        elif char == "*":
            toks.append(MUL_TOK())
        elif char == "(":
            toks.append(LEFT_PAREN_TOK())
        elif char == ")":
            toks.append(RIGHT_PAREN_TOK())
        elif char == " ":
            toks.append(SPACE_TOK())
        else:
            colorized_string = f"{bcolors.OKCYAN}{bcolors.BOLD}\"{input_str[:input_str.index(char)]}{bcolors.ENDC}{bcolors.FAIL}{bcolors.UNDERLINE}{input_str[input_str.index(char)]}{bcolors.ENDC}{bcolors.OKCYAN}{bcolors.BOLD}{input_str[input_str.index(char)+1:]}\"{bcolors.ENDC}"
            error_desc = f"{bcolors.MAGENTA}Cannot tokenize string due to invalid char: {colorized_string}"
            raise TokenizerError(error_desc)
        last_char_type = str
        
    if last_char_type == int:
        toks.append(INT_TOK(int(int_buffer)))
        
    toks.append(EOS_TOK())
    return toks

# Parse an input string using a parsing table
def parse(input_str: str, parsing_table: dict) -> None:
    # Tokenize input string
    toks = tokenize(input_str)
    stack = []
    toks_pointer = 0

    # Push start symbol to stack
    # Start symbol is the LHS of the first rule in the parsing table
    stack.append(next(iter(parsing_table)))

    # Parse until stack is empty
    while stack:
        # Skip space tokens
        if (type(toks[toks_pointer]) == SPACE_TOK):
            toks_pointer += 1
            continue

        # Check if top of stack is a terminal matching the current tok in toks
        if type(toks[toks_pointer]) == stack[-1]:
            stack.pop()
            toks_pointer += 1
            continue
        # Raise error if terminals do not match
        elif issubclass(BASE_TOK, type(toks[toks_pointer])):
            colorized_string = rebuild_and_mark_error(toks, toks_pointer)
            error_desc = f"{bcolors.MAGENTA}Expected token {bcolors.OKCYAN}{bcolors.BOLD}\"{stack[-1].value}\"{bcolors.ENDC}{bcolors.MAGENTA} but got: {colorized_string}"
            raise ParserError(error_desc)

        # Check if production for top of stack exists in parsing table
        if (parsing_table.get(stack[-1])).get(type(toks[toks_pointer])) == None:
            colorized_string = rebuild_and_mark_error(toks, toks_pointer)
            error_desc = f"{bcolors.MAGENTA}Unexpected token generated by: {colorized_string}"
            raise ParserError(error_desc)

        # Lookup corresponding production to push on stack and pop the current top
        stack.extend(reversed(parsing_table[stack.pop()][type(toks[toks_pointer])]))

    # Check if tokens were not exhausted
    if toks_pointer != len(toks)-1:
        colorized_string = rebuild_and_mark_error(toks, toks_pointer)
        error_desc = f"{bcolors.MAGENTA}Extra token generated by: {colorized_string}"
        raise ParserError(error_desc)

if __name__ == "__main__":
    input_strs = []

    for arg in sys.argv[1:]:
        # Check if argument has .txt extension
        if arg.endswith(".txt"):
            if os.path.isfile(arg):
                with open(arg) as file:
                    input_strs.extend(file.read().splitlines())
            # Print a warning if file does not exist
            else:
                print(f"{bcolors.WARNING}WARNING: File {bcolors.BOLD}{arg}{bcolors.ENDC}{bcolors.WARNING} does not exist, skipping argument{bcolors.ENDC}")
        # Store argument as input string
        else:
            input_strs.append(arg)
    
    # Check if input_strs is empty
    if (not input_strs):
        print(f"\n{bcolors.MAGENTA}{bcolors.BOLD}Error: {bcolors.ENDC}{bcolors.MAGENTA}No strings passed to parse")
        print(f"Please pass a raw string or a txt file containing the strings to parse as command line arguments{bcolors.ENDC}")
        exit(0)

    print(f"\nPARSING RESULTS\n")

    for str in input_strs:
        try:
            print(f"String: {bcolors.OKCYAN}{bcolors.BOLD}\"{str}\"{bcolors.ENDC}")
            parse(str, parsing_table)

            # On successful parsing
            print(f"{bcolors.OKGREEN}Valid String{bcolors.ENDC}")
            print("\n")

        except TokenizerError as e:
            print(f"Encountered error: {bcolors.FAIL}TokenizerError{bcolors.ENDC}")
            print(f"Error Details: {e}")
            print("\n")
        except ParserError as e:
            print(f"Encountered error: {bcolors.FAIL}ParserError{bcolors.ENDC}")
            print(f"Error Details: {e}")
            print("\n")