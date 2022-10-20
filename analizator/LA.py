from cmath import inf
import ntpath
import sys
import os
import pprint

sys.path.insert(0,'..')

import GLA
from SimEnka import Enka

class Lex:
    def __init__(self, enka_definitions_dir):
        self.actions_fname = ""
        self.enka_definitions_fnames = []
        self.enkas_dict = {}
        
        self.actions_dict = {}
        self.start_state = ""

        self.LINE_SEPARATOR = GLA.LINE_SEPARATOR
        self.INLINE_SEPARATOR = GLA.INLINE_SEPARATOR

        self.__get_fnames_from_dir(enka_definitions_dir)
        self.__load_enkas()
        self.__load_actions()
        self.__parse_actions()

        self.current_state = self.start_state
        self.start_of_expression = 0
        self.end_of_expression = inf
        self.current_pos = 0

        self.input_string = ""
        self.length_of_input = 0
        self.current_row = 1

        self.active_enkas = {}

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
                self.enkas_dict[enka_name] = Enka(definition.read().split(self.LINE_SEPARATOR), 0)
        return

    def __load_actions(self):
        with open(self.actions_fname, 'r') as actions_defitions:
            lines = actions_defitions.read().split(self.LINE_SEPARATOR)
            lines = [line for line in lines if line != '']
            self.start_state = lines[0]
            for line in lines[1:]:
                state, list_of_actions = line.split(':')
                list_of_actions = list_of_actions.split(self.INLINE_SEPARATOR)
                # skip the { }
                self.actions_dict[state] = list_of_actions[1:-1]
        return

    def __parse_actions(self):
        for action_name in self.actions_dict:
            actions_list = self.actions_dict[action_name]
            [lex_unit] = [action for action in actions_list if not (action.startswith("NOVI_REDAK") or action.startswith("UDJI_U_STANJE") or action.startswith("VRATI_SE"))]
            
            newline_l = [action for action in actions_list if action.startswith('NOVI_REDAK')]
            add_newline = True if len(newline_l) == 1 else False

            new_state_l = [action for action in actions_list if action.startswith('UDJI_U_STANJE')]
            [new_state] = new_state_l if len(new_state_l) == 1 else ['-']

            go_back_to_l = [action for action in actions_list if action.startswith('VRATI_SE')]
            [go_back_to] = go_back_to_l if len(go_back_to_l) == 1 else ['-']

            self.actions_dict[action_name] = {
                'lex_unit': None if lex_unit == '-' else lex_unit,
                'add_newline': add_newline,
                'new_state': None if new_state == '-' else "<" + new_state.split(' ')[-1] + ">",
                'go_back_to': None if go_back_to == '-' else int(go_back_to.split(' ')[-1])
            }
        return


    def __restart_enkas_from_pos(self, pos):
        for enka_name in self.active_enkas:
            self.active_enkas[enka_name].restart_from_pos(pos)
        return

    def __enter_state_at_pos(self, new_state, pos):
        self.active_enkas = {k:v for k, v in self.enkas_dict.items() if k.startswith(new_state)}
        self.__restart_enkas_from_pos(pos)
        return

    def __do_actions(self, enka_name):
        actions = self.actions_dict[enka_name]
        entered_state = False
        
        if actions['go_back_to'] is not None:
            self.end_of_expression = self.start_of_expression + actions['go_back_to']

        if actions['lex_unit'] is not None:
            lexeme = self.input_string[self.start_of_expression:self.end_of_expression]
            if lexeme != '':
                self.output.append((actions['lex_unit'], self.current_row, lexeme))
            
        if actions['new_state'] is not None:
            self.__enter_state_at_pos(actions['new_state'], self.end_of_expression)
            entered_state = True

        if actions['add_newline']:
            self.current_row += 1

        if not entered_state:
            self.__restart_enkas_from_pos(self.end_of_expression)

        self.start_of_expression = self.end_of_expression
        self.end_of_expression = inf
        self.current_pos = self.start_of_expression

        return

    def __feed_character_to_active_enkas(self, character):
        for enka_name in self.active_enkas:
            self.active_enkas[enka_name].feed_next_character(character)
        return

    def __check_if_all_enkas_terminated(self):
        for enka_name in self.active_enkas:
            if not self.active_enkas[enka_name].has_terminated():
                return False
        return True

    def __pick_highest_priority_enka(self):
        all_enkas = self.active_enkas.items()
        dist_max = max([enka.get_furthest_pos() for (_, enka) in all_enkas])
        enkas_with_max_dist = [enka_name for (enka_name, enka) in all_enkas if enka.get_furthest_pos() == dist_max]
        enkas_with_max_dist_sort = sorted(enkas_with_max_dist)
        highest_priority_enka_name = enkas_with_max_dist_sort[0]
        [highest_priority_enka] = [enka for enka_name, enka in all_enkas if enka_name == highest_priority_enka_name]
        return (highest_priority_enka_name, highest_priority_enka)

    def compute_from_string(self, input_string):
        self.input_string = input_string
        self.length_of_input = len(self.input_string)
        self.__enter_state_at_pos(self.start_state, 0)

        # print(self.input_string[20:28])

        while self.current_pos < self.length_of_input:
            c = input_string[self.current_pos]
            print("-----------")
            print(f"|Pos: {self.current_pos}, Char: {c}|")
            # try:
            #     c = input_string[self.current_pos]
            # except TypeError:
            #     print('a')
            #     print(self.current_pos)
            #     print(self.input_string)
            #     sys.exit()
            
            self.__feed_character_to_active_enkas(c)
            if self.__check_if_all_enkas_terminated():
                enka_name, enka = self.__pick_highest_priority_enka()
                print(f"Enka {enka_name} terminated at |Pos: {self.current_pos}, Char: {c}|")
                furthest_pos = enka.get_furthest_pos()
                if furthest_pos == -inf:
                    self.current_pos += 1
                    self.start_of_expression = self.current_pos
                    self.end_of_expression = inf
                    self.__restart_enkas_from_pos(self.current_pos)
                    continue
                self.end_of_expression = enka.get_furthest_pos() + 1
                self.__do_actions(enka_name)
            else:
                self.current_pos += 1
            print("-----------")

        return

    def output_as_string(self):
        return '\n'.join([tup[0] + ' ' + str(tup[1]) + ' ' + tup[2] for tup in self.output]) + '\n'
    
    # def __set_active_enkas(self):
    #     # print(self.current_state)
    #     # print(self.enkas_dict)
    #     self.active_enkas = {k:v for (k, v) in self.enkas_dict.items() if k.startswith(self.current_state)}
    #     for state in self.active_enkas:
    #         self.active_enkas[state].restart()
    #         self.active_enkas[state].set_current_pos(self.current_pos)

    #     return

    # def __reset_enkas(self):
    #     for state in self.active_enkas:
    #         self.active_enkas[state].restart()
    #         self.active_enkas[state].set_current_pos(self.current_pos)
    #         self.active_enkas[state].set_furthest_pos(-inf)


    # def __do_actions(self, list_of_actions, lexem, furthest_pos):
    #     for i, action in enumerate(list_of_actions):
    #         if i == 0:
    #             unif_char = action
    #             if unif_char != '-':
    #                 self.output.append((unif_char, self.current_row, lexem))
    #             elif len(list_of_actions) == 1:
    #                 self.start_of_expression = furthest_pos + 1
    #                 self.current_pos = self.start_of_expression
    #                 self.__reset_enkas()

    #         if 'NOVI_REDAK' in action:
    #             self.current_row += 1
    #             self.start_of_expression = furthest_pos + 1
    #             self.current_pos = self.start_of_expression
    #             self.__reset_enkas()
    #             # ostani u istom stanju, 
    #             # pomakni se na sljedeći znak,
    #             # resetiraj enka-ove
    #         elif 'UDJI_U_STANJE' in action:
    #             self.start_of_expression = furthest_pos + 1
    #             self.current_pos = self.start_of_expression
    #             to_enter = action.split(' ')[1]
    #             self.current_state = "<" + to_enter + ">"
    #             self.__set_active_enkas()
    #         elif 'VRATI_SE' in action:
    #             to_group = int(action.split(' ')[1])
    #             self.current_pos = self.start_of_expression + to_group
    #             self.__set_active_enkas()
                
    #     return

    # def compute_from_string(self, input_string):
    #     self.input_string = input_string
    #     # print(self.input_string)
    #     self.length_of_input = len(input_string)

    #     self.__set_active_enkas()

    #     while self.current_pos < self.length_of_input:
    #         # print("-----------")
    #         # print("Before the character, enkas look like: ")
    #         # pprint.pprint(self.active_enkas)
    #         # print("END OF ENKAS")


    #         # print(f"Current position: {self.current_pos}")
    #         c = self.input_string[self.current_pos]
    #         # print(f'Character: |{c}|')

    #         for state in self.active_enkas:
    #             # print(state, self.active_enkas[state])
    #             self.active_enkas[state].feed_next_character(c)
    #             # print(state, self.active_enkas[state])

    #             # last matched regex
    #             # if self.active_enkas[state][0].is_in_acceptable_state():
    #             #     self.active_enkas[state][1] = self.current_pos
        
    #         # print("Now enkas look like: ")
    #         # pprint.pprint(self.active_enkas)
    #         # print("END OF ENKAS")

    #         if all([enka.is_in_end_state() for enka in self.active_enkas.values()]):
    #             # print('END OF LEXEME')

    #             if self.current_pos == self.length_of_input - 1 and all([enka.get_furthest_pos() == -inf for enka in self.active_enkas.values()]):
    #                 # oporavi se od pogreske
    #                 pass

    #             else:
    #                 # print(self.output)
    #                 # print(self.active_enkas.items())
    #                 enka_name, _ = max(self.active_enkas.items(), key=lambda tup: tup[1].get_furthest_pos())
    #                 furthest_pos = self.active_enkas[enka_name].get_furthest_pos()
    #                 # print(enka_name, furthest_pos)
    #                 lexem = self.input_string[self.start_of_expression:(furthest_pos + 1)]
    #                 list_of_actions = self.actions_dict[enka_name]
    #                 # print(lexem, list_of_actions)

    #                 self.__do_actions(list_of_actions, lexem, furthest_pos)

    #         else:
    #             self.current_pos += 1

    #     return

    def __repr__(self):
        return pprint.pformat(vars(self), indent=2, width=200, compact=True)


def main():
    dir = '../integration_tests/'
    dir_names = [os.path.abspath(os.path.join(dir, name))[:-3] for name in os.listdir(dir) if name.endswith('.in')]

    dir_names = [name for name in dir_names if 'svaki_drugi_a2' in name]

    # Working: minusLang, nadji_a1, nadji_a2, svaki_drugi_a1, svaki_drugi_a2
    # Not working: simplePpjLang

    for dir_name in dir_names:
        tablice_dir_name = os.path.join(dir_name, 'tablice/')
        lex = Lex(tablice_dir_name)
        computed = ''
        output = ''
        with open(dir_name + '.in') as input_file:
            lex.compute_from_string(input_file.read())
            computed = lex.output_as_string()
        print(computed)
        print("----------------------")
        with open(dir_name + '.out') as output_file:
            output = output_file.read()
        print(output)
        print("----------------------")

        assert output == computed

if __name__ == '__main__':
    main()