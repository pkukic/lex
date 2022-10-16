from cmath import inf
import ntpath
import sys
import os

from SimEnka import Enka

class Lex:
    def __init__(self, enka_definitions_dir):
        self.actions_fname = ""
        self.enka_definitions_fnames = []
        self.enkas_dict = {}
        
        self.actions_dict = {}
        self.start_state = ""

        self.__get_fnames_from_dir(enka_definitions_dir)
        self.__load_enkas()
        self.__load_actions()

        self.current_state = self.start_state
        self.start_of_expression = 0
        self.end_of_expression = inf
        self.current_pos = 0
        self.active_enkas = {}

        self.input_string = ""
        self.length_of_input = 0

        return

    def __get_fnames_from_dir(self, dir):
        dir_abspath = os.path.abspath(dir)
        abs_fnames = [os.path.join(dir_abspath, fname) for fname in os.listdir(dir_abspath)]
        for fname in abs_fnames:
            if 'akcije' in ntpath.basename(fname):
                self.actions_fname = fname
            else:
                self.enka_definitions_fnames.append(fname)
        return

    def __load_enkas(self):
        for fname in self.enka_definitions_fnames:
            with open(fname, 'r') as definition:
                enka_name = ntpath.basename(fname).split('.')[0]
                self.enkas_dict[enka_name] = Enka(definition.read().splitlines())
        return

    def __load_actions(self):
        with open(self.actions_fname, 'r') as actions_defitions:
            lines = actions_defitions.read().splitlines()
            self.start_state = lines[0]
            for line in lines[1:]:
                state, list_of_actions = line.split(':')
                list_of_actions = list_of_actions.split(',')
                self.actions_dict[state] = list_of_actions
        return

    def __set_active_enkas(self):
        self.active_enkas = {k:(v, -inf) for (k, v) in self.enkas_dict.items() if k.startswith(self.current_state)}

    def compute_from_string(self, input_string):
        # initialize pointers
        # move pointers
        # pointer array (for each enka)
        # once all enka have terminated, remember the one with the top priority

        self.input_string = input_string
        self.length_of_input = len(input_string)

        while self.current_pos < self.length_of_input:
            
            self.__set_active_enkas()
            c = self.input_string[self.current_pos]

            for state in self.active_enkas:
                self.active_enkas[state][0].feed_next_character(c)
                if self.active_enkas[state][0].is_in_acceptable_state():
                    self.active_enkas[state][1] = self.current_pos

            if all(self.active_enkas.values(), lambda tup: tup[0].is_in_end_state()):
                furthest_acceptable_state_at = max(self.active_enkas.values(), lambda tup: tup[1])
                if self.current_pos != self.length_of_input - 1:
                    # oporavak od pogreske
                    pass
                else:
                    # formiraj leksem
                    # napravi akcije
                    pass
        return


if __name__ == '__main__':
    input_string = sys.stdin.read()
    lex = Lex()
    print(lex.compute_from_string(input_string), end='')