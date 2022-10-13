import sys
import os

from SimEnka import Enka

class Lex:
    def __init__(self, enka_definitions_dir):
        self.enka_dict = Lex.__load_enkas_from_definitions_dir(enka_definitions_dir)

        # load start state
        # load actions

    @classmethod
    def __load_enkas_from_definitions_dir(definitions_dir):
        definitions_dir_abs = os.path.abspath(definitions_dir)
        fnames = list(os.listdir(definitions_dir_abs))
        enkas = {}
        for fname in fnames:
            abs_fname = os.path.join(definitions_dir_abs, fname)
            without_file_extension, _ = fname.split('.')
            state, number = without_file_extension.split('_')
            with open(abs_fname, 'r') as enka_definition:
                enkas[f"{state}_{number}"] = Enka(enka_definition.read().splitlines())
        return enkas        

    # def parse_actions(...)

    def compute_from_string(input_string):
        # initialize pointers
        # move pointers
        # pointer array (for each enka)
        # once all enka have terminated, remember the one with the top priority

        pass


if __name__ == '__main__':
    input_string = sys.stdin.read()
    lex = Lex()
    print(lex.compute_from_string(input_string), end='')