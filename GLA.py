from state_machine import StateMachine, Transition
from regex_prep import RegexPrep
import os

TARGET = "target.lan"
LINE_SEPARATOR = "(###&&&???%%%***)\n"
INLINE_SEPARATOR = "(&&%%??**)"
STATE_TRANSITION_SEPARATOR = "(%%%%->%%%%)"


def generate_eNKA_tables():
    working_dir = os.path.join('.', 'analizator')
    working_dir = os.path.join(working_dir, 'tablice')
    with open(os.path.join(working_dir, "akcije.txt"), 'w') as actions:
        with open(TARGET, 'r') as file:
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

                    with open(os.path.join(working_dir, state) + ".txt", 'w') as wf:
                        # skip first line
                        wf.write(LINE_SEPARATOR)
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
    # read from stdin -> convert to target.lan file
    rp = RegexPrep(TARGET)
    rp.start()
    # read fomr TARGET and generate eNKA definitions in ./analizator/tablice
    generate_eNKA_tables()

if __name__ == '__main__':
    main()