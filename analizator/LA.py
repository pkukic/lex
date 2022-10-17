from cmath import inf
from multiprocessing.dummy import active_children
import ntpath
import sys
import os
import pprint

sys.path.insert(0,'..')

from SimEnka import Enka
from GLA import LINE_SEPARATOR, INLINE_SEPARATOR

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
        self.current_row = 1

        self.output = []

        return

    def __get_fnames_from_dir(self, dir):
        dir_abspath = os.path.abspath(dir)
        abs_fnames = [os.path.join(dir_abspath, fname) for fname in os.listdir(dir_abspath)]
        for fname in abs_fnames:
            if 'akcije' in ntpath.basename(fname):
                self.actions_fname = fname
            elif ntpath.basename(fname).endswith('.txt') and 'target' not in ntpath.basename(fname):
                self.enka_definitions_fnames.append(fname)
        return

    def __load_enkas(self):
        for fname in self.enka_definitions_fnames:
            with open(fname, 'r') as definition:
                enka_name = ntpath.basename(fname).split('.')[0]
                self.enkas_dict[enka_name] = Enka(definition.read().split(LINE_SEPARATOR))
        return

    def __load_actions(self):
        with open(self.actions_fname, 'r') as actions_defitions:
            lines = actions_defitions.read().split(LINE_SEPARATOR)
            lines = [line for line in lines if line != '']
            # print(lines)
            self.start_state = lines[0]
            for line in lines[1:]:
                state, list_of_actions = line.split(':')
                list_of_actions = list_of_actions.split(INLINE_SEPARATOR)
                self.actions_dict[state] = list_of_actions
        return

    def __set_active_enkas(self):
        # print(self.current_state)
        # print(self.enkas_dict)
        self.active_enkas = {k:(v, -inf) for (k, v) in self.enkas_dict.items() if k.startswith(self.current_state)}
        for state in self.active_enkas:
            self.active_enkas[state][0].restart()
        return

    def __do_actions(self, list_of_actions, lexem):
        for i, action in enumerate(list_of_actions):
            if i == 0:
                unif_char = action
                if unif_char != '-':
                    self.output.append(unif_char, self.current_row, lexem)

            if 'NOVI_REDAK' in action:
                self.current_row += 1
            elif 'UDJI_U_STANJE' in action:
                to_enter = action.split(' ')[1]
                self.current_state = to_enter
                self.__set_active_enkas()
            elif 'VRATI_SE' in action:
                to_group = int(action.split(' ')[1])
                self.current_pos = self.start_of_expression + to_group
                self.__set_active_enkas()
        
        return

    def compute_from_string(self, input_string):
        self.input_string = input_string
        print(self.input_string)
        self.length_of_input = len(input_string)

        while self.current_pos < self.length_of_input:
            print(self.current_pos)
            
            self.__set_active_enkas()
            print(self.active_enkas)
            c = self.input_string[self.current_pos]
            print(c)

            for state in self.active_enkas:
                print(state, self.active_enkas[state])
                self.active_enkas[state][0].feed_next_character(c)
                if self.active_enkas[state][0].is_in_acceptable_state():
                    self.active_enkas[state][1] = self.current_pos

            if all(list(filter(lambda tup: tup[0].is_in_end_state(), self.active_enkas.values()))):
                print('here')
                if self.current_pos != self.length_of_input - 1:
                    self.current_pos = self.start_of_expression + 1
                    self.start_of_expression = self.current_pos
                    self.current_state = self.start_state
                    self.__set_active_enkas()
                else:
                    # print(self.output)
                    # print(self.active_enkas.items())
                    enka_name, (enka, furthest_pos) = max(self.active_enkas.items(), key=lambda tup: tup[1][1])
                    print(furthest_pos)
                    lexem = self.input_string[self.start_of_expression:(furthest_pos + 1)]
                    list_of_actions = self.actions_dict[enka_name]
                    self.__do_actions(list_of_actions, lexem)
        return

    def __repr__(self):
        return pprint.pformat(vars(self), indent=2, width=120, compact=True)


def main():
    dir = '../integration_tests/'
    dir_names = [os.path.abspath(os.path.join(dir, name))[:-3] for name in os.listdir(dir) if name.endswith('.in')]

    # print(dir_names)

    for dir_name in dir_names:
        tablice_dir_name = os.path.join(dir_name, 'tablice/')
        lex = Lex(tablice_dir_name)
        print(lex)
        with open(dir_name + '.in') as input:
            lex.compute_from_string(input.read())
        print(lex)

if __name__ == '__main__':
    main()