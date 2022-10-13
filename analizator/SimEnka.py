from pprint import pformat
import sys

class Automaton:
    def __init__(self):
        self.rules_dict = {}
        self.input_strings = []
        self.input_characters_list = []
        self.input_characters = []
        self.states = []
        self.characters = []
        self.acceptable_states = []
        self.start_state = ''
        self.current_states = []
        self.states_history = []
        self.output_string = ''
        self.output_strings_list = []

    def clear_history(self):
        self.current_states = []
        self.states_history = []
        self.output_string = ''

    def add_to_rules_dict(self, rule):
        state_and_input, output = rule.split('->')
        state, input = state_and_input.split(',')
        output_states = output.split(',')
        self.rules_dict[(state, input)] = output_states
        return

    def parse(self, input_lines):
        input, states, characters, acceptable_states, start_state = input_lines[:5]
        rules = input_lines[5:]

        self.input_strings = input.split('|')
        self.input_characters_list = [string.split(',') for string in self.input_strings]
        self.states = states.split(',')
        self.characters = characters.split(',')
        self.acceptable_states = acceptable_states.split(',')
        self.start_state = start_state

        for rule in rules:
            self.add_to_rules_dict(rule)
        return

    def get_eps_states(self, states_to_be_evaluated):
        eps_states = []
        for state in states_to_be_evaluated:
            eps_states += self.rules_dict.get((state, '$'), [None])
        return eps_states

    def prune_eps_states(self, eps_states):
        pruned_states = []
        for state in eps_states:
            if state not in self.current_states and state is not None and state != '#':
                pruned_states.append(state)
        return list(set(pruned_states))

    def compute_eps_states(self, states_to_be_evaluated):
        return self.prune_eps_states(self.get_eps_states(states_to_be_evaluated))

    def epsilon_step(self):
        states_to_be_evaluated = self.current_states
        while len(states_to_be_evaluated) > 0:
            computed_states = self.compute_eps_states(states_to_be_evaluated)
            self.current_states += computed_states
            states_to_be_evaluated = computed_states
        return

    def get_transition_states(self, input):
        transition_states = []
        for state in self.current_states:
            transition_states += self.rules_dict.get((state, input), [None])
        return transition_states

    def prune_transition_states(self, transition_states):
        pruned_states = []
        for state in transition_states:
            if state is not None and state != '#':
                pruned_states.append(state)
        return list(set(pruned_states))

    def compute_transition_states(self, input):
        return self.prune_transition_states(self.get_transition_states(input))

    def simulate(self):
        self.current_states.append(self.start_state)
        for input in self.input_characters:
            self.epsilon_step()
            self.record_history()
            transition_states = self.compute_transition_states(input)
            if len(transition_states) == 0:
                transition_states = ['#']
            self.current_states = transition_states
        self.epsilon_step()
        self.record_history()
        return

    def record_history(self):
        self.states_history.append(self.current_states)
        return

    def output_for_input_string(self):
        return '|'.join([','.join(sorted(state_list)) for state_list in self.states_history])

    def compute(self, input_lines):
        self.parse(input_lines)
        for input_characters in self.input_characters_list:
            self.clear_history()
            self.input_characters = input_characters
            self.simulate()
            self.output_string = self.output_for_input_string()
            self.output_strings_list.append(self.output_string)
        return

    def compute_from_string(self, file_as_string):
        input_lines = file_as_string.split('\n')
        input_lines = [line for line in input_lines if line != '']
        self.compute(input_lines)
        output_string = '\n'.join(self.output_strings_list)
        output_string += '\n'
        return output_string

    def __repr__(self):
        return pformat(vars(self), indent=2, width=120)


if __name__ == '__main__':
    a = Automaton()
    input_string = sys.stdin.read()
    print(a.compute_from_string(input_string), end='')