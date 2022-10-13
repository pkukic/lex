import sys

class Lex:
    pass

if __name__ == '__main__':
    input_string = sys.stdin.read()
    lex = Lex()
    print(lex.compute_from_string(input_string), end='')