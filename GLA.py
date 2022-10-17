from state_machine import StateMachine, Transition
from regex_prep import RegexPrep
import os

LINE_SEPARATOR = "(###&&&???%%%***)\n"
INLINE_SEPARATOR = "(&&%%??**)"
STATE_TRANSITION_SEPARATOR = "(%%%%->%%%%)"


def generate_eNKA_tables(beginning_state: str, working_dir):
    print(working_dir)
    with open(os.path.join(working_dir, "akcije.txt"), 'w+') as actions:
        actions.write(beginning_state + LINE_SEPARATOR)
        with open(os.path.join(working_dir, "target.lan"), 'r') as file:
            n = 0
            state = ""
            for line in file.readlines():
                if line.startswith("<"):
                    # generate new state machine
                    index = line.find(">")
                    name = line[:index + 1]

                    sm = StateMachine()
                    start_state, end_state = sm.translate(line[index + 1: -1])
                    sm.start_state = start_state
                    sm.end_state = end_state
                    state = name + str(n)

                    with open(os.path.join(working_dir, state) + ".txt", 'w+') as wf:
                        # write all of the states in a single line
                        for i in range(0, sm.number_of_states):
                            wf.write(str(i))
                            if i != sm.number_of_states - 1:
                                wf.write(INLINE_SEPARATOR)
                            else:
                                wf.write(LINE_SEPARATOR)
                        # write all of the symbols in a single line
                        for sym, i in zip(sm.symbols, range(0, len(sm.symbols))):
                            wf.write(sym)
                            if i != len(sm.symbols) - 1:
                                wf.write(INLINE_SEPARATOR)
                            else:
                                wf.write(LINE_SEPARATOR)
                        # write the begining state in new line
                        wf.write(str(sm.start_state) + LINE_SEPARATOR)
                        # write the end (acceptable) state in new line
                        wf.write(str(sm.end_state) + LINE_SEPARATOR)

                        # write all of the transitions
                        for transition in sm.transitions:
                            wf.write(str(transition.start) + INLINE_SEPARATOR + transition.char + STATE_TRANSITION_SEPARATOR + str(transition.end) + LINE_SEPARATOR)
                    
                    actions.write(state + ":")
                    n += 1
                elif line.startswith("}"):
                    actions.write(line[:-1] + LINE_SEPARATOR)
                else:
                    actions.write(line[:-1] + INLINE_SEPARATOR)

def main():
    dir = './integration_tests/'
    dir_names = [os.path.abspath(os.path.join(dir, name))[:-3] for name in os.listdir(dir) if name.endswith('.in')]

    # print(dir_names)

    for dir_name in dir_names:

        tablice_dir_name = os.path.join(dir_name, 'tablice/')

        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        
        if not os.path.exists(tablice_dir_name):
            os.mkdir()
        
        rp = RegexPrep(os.path.join(tablice_dir_name, 'target.lan'), dir_name + '.lan')
        beginning_state = rp.start()
        generate_eNKA_tables(beginning_state, tablice_dir_name)


if __name__ == '__main__':
    main()