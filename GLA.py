from state_machine import StateMachine, Transition
from regex_prep import RegexPrep

TARGET = "target.lan"


def generate_eNKA_tables():
    with open(TARGET, 'r') as file:
        for line in file.readlines():
            if line.startswith("<"):
                # generate new state machine
                index = line.find(">")
                sm = StateMachine()
                start_state, end_state = sm.translate(line[index + 1: -1])
                sm.start_state = start_state
                sm.end_state = end_state
                for transition in sm.transitions:
                    print(str(transition.start) + "," + transition.char + "->" + str(transition.end))
            elif line.startswith("%X"):
                pass
            elif line.startswith("%L"):
                pass
            elif line.startswith("}"):
                pass

def main():
    # TODO read from stdin
    rp = RegexPrep("./integration/lab1_ppjLang.lan", TARGET)
    rp.start()
    generate_eNKA_tables()

if __name__ == '__main__':
    main()