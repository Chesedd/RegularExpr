class NFA:
    def __init__(self):
        self.initial = None
        self.final = None
        self.transitions = dict()  # (from_state, symbol) -> set of to_states
        self.states = set()

    def copy_with_remap(self, remap):
        new_nfa = NFA()
        new_nfa.initial = remap[self.initial]
        new_nfa.final = remap[self.final]
        new_nfa.states = {remap[s] for s in self.states}
        new_nfa.transitions = {}
        for (fr, sym), to_set in self.transitions.items():
            new_fr = remap[fr]
            new_to_set = {remap[t] for t in to_set}
            key = (new_fr, sym)
            if key not in new_nfa.transitions:
                new_nfa.transitions[key] = set()
            new_nfa.transitions[key].update(new_to_set)
        return new_nfa

    @staticmethod
    def from_symbol(symbol):
        nfa = NFA()
        nfa.initial = 0
        nfa.final = 1
        nfa.states = {0, 1}
        nfa.transitions = {(0, symbol): {1}}
        return nfa

    def concat(self, other):
        if not self.states:
            return other
        if not other.states:
            return self
        max_self = max(self.states)
        remap_other = {s: s + max_self + 1 for s in other.states}
        other_remapped = other.copy_with_remap(remap_other)
        new_nfa = NFA()
        new_nfa.initial = self.initial
        new_nfa.final = other_remapped.final
        new_nfa.states = self.states.union(other_remapped.states)
        new_nfa.transitions = {**self.transitions, **other_remapped.transitions}
        eps_key = (self.final, None)
        new_nfa.transitions[eps_key] = new_nfa.transitions.get(eps_key, set()).union(
            {other_remapped.initial}
        )
        return new_nfa

    def union(self, other):
        if not self.states:
            return other
        if not other.states:
            return self
        remap_self = {s: s + 1 for s in self.states}
        self_remapped = self.copy_with_remap(remap_self)
        max_self = max(self_remapped.states)
        remap_other = {s: s + max_self + 1 for s in other.states}
        other_remapped = other.copy_with_remap(remap_other)
        new_nfa = NFA()
        new_nfa.initial = 0
        new_final = max(other_remapped.states) + 1
        new_nfa.final = new_final
        new_nfa.states = (
            {0, new_final}.union(self_remapped.states).union(other_remapped.states)
        )
        new_nfa.transitions[(0, None)] = {self_remapped.initial, other_remapped.initial}
        new_nfa.transitions[(self_remapped.final, None)] = {new_final}
        new_nfa.transitions[(other_remapped.final, None)] = {new_final}
        new_nfa.transitions.update(self_remapped.transitions)
        new_nfa.transitions.update(other_remapped.transitions)
        return new_nfa

    def kleene_star(self):
        new_nfa = NFA()
        if not self.states:
            return new_nfa
        remap = {s: s + 1 for s in self.states}
        self_remapped = self.copy_with_remap(remap)
        new_initial = 0
        new_final = max(self_remapped.states) + 1
        new_nfa.initial = new_initial
        new_nfa.final = new_final
        new_nfa.states = {new_initial, new_final}.union(self_remapped.states)
        new_nfa.transitions[(new_initial, None)] = {self_remapped.initial, new_final}
        new_nfa.transitions[(self_remapped.final, None)] = {
            self_remapped.initial,
            new_final,
        }
        new_nfa.transitions.update(self_remapped.transitions)
        return new_nfa


class DFA:
    def __init__(self, initial, finals, transitions, alphabet, states_count):
        self.initial = initial
        self.finals = finals
        self.transitions = transitions
        self.alphabet = alphabet
        self.states = set(range(states_count))

    def minimize(self):
        P = [self.finals, self.states - self.finals]
        W = [self.finals.copy(), (self.states - self.finals).copy()]
        while W:
            A = W.pop(0)
            for c in self.alphabet:
                X = set()
                for state in self.states:
                    if self.transitions.get((state, c), -1) in A:
                        X.add(state)
                for Y in P.copy():
                    intersect = Y & X
                    diff = Y - X
                    if intersect and diff:
                        P.remove(Y)
                        P.append(intersect)
                        P.append(diff)
                        if Y in W:
                            W.remove(Y)
                            W.append(intersect)
                            W.append(diff)
                        else:
                            if len(intersect) <= len(diff):
                                W.append(intersect)
                            else:
                                W.append(diff)
        state_to_group = {}
        for i, group in enumerate(P):
            for state in group:
                state_to_group[state] = i
        new_transitions = {}
        for (s, c), d in self.transitions.items():
            new_s = state_to_group[s]
            new_d = state_to_group[d]
            new_transitions[(new_s, c)] = new_d
        new_initial = state_to_group[self.initial]
        new_finals = {state_to_group[s] for s in self.finals}
        return DFA(
            initial=new_initial,
            finals=new_finals,
            transitions=new_transitions,
            alphabet=self.alphabet,
            states_count=len(P),
        )


def tokenize_regex(regex):
    tokens = []
    stack = []
    for c in regex:
        if c == "(":
            stack.append(c)
        elif c == ")":
            if not stack:
                raise ValueError("Unbalanced parentheses")
            stack.pop()
        tokens.append(c)
    if stack:
        raise ValueError("Unbalanced parentheses")
    new_tokens = []
    for i in range(len(tokens) - 1):
        new_tokens.append(tokens[i])
        current = tokens[i]
        next_tok = tokens[i + 1]
        if current not in ("(", "|") and next_tok not in ("*", "|", ")"):
            new_tokens.append("·")
    new_tokens.append(tokens[-1])
    return new_tokens


def shunting_yard(tokens):
    precedence = {"*": 3, "·": 2, "|": 1, "(": 0}
    output = []
    stack = []
    for token in tokens:
        if token == "(":
            stack.append(token)
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            stack.pop()
        elif token in precedence:
            while stack and precedence.get(stack[-1], 0) >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        else:
            output.append(token)
    while stack:
        output.append(stack.pop())
    return output


def build_nfa(postfix):
    stack = []
    for token in postfix:
        if token == "*":
            nfa = stack.pop()
            stack.append(nfa.kleene_star())
        elif token == "·":
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(nfa1.concat(nfa2))
        elif token == "|":
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(nfa1.union(nfa2))
        else:
            stack.append(NFA.from_symbol(token))
    return stack[0] if stack else NFA()


def epsilon_closure(nfa, states):
    closure = set(states)
    stack = list(states)
    while stack:
        state = stack.pop()
        key = (state, None)
        if key in nfa.transitions:
            for s in nfa.transitions[key]:
                if s not in closure:
                    closure.add(s)
                    stack.append(s)
    return closure


def move(nfa, states, symbol):
    next_states = set()
    for state in states:
        key = (state, symbol)
        if key in nfa.transitions:
            next_states.update(nfa.transitions[key])
    return next_states


def nfa_to_dfa(nfa):
    alphabet = set()
    for state, symbol in nfa.transitions:
        if symbol is not None:
            alphabet.add(symbol)
    if not alphabet:
        alphabet.add("")
    alphabet = sorted(alphabet)
    initial_states = epsilon_closure(nfa, {nfa.initial})
    dfa_states = [initial_states]
    dfa_transitions = {}
    state_map = {frozenset(initial_states): 0}
    stack = [initial_states]
    finals = []
    if nfa.final in initial_states:
        finals.append(0)
    while stack:
        current = stack.pop()
        current_key = frozenset(current)
        for symbol in alphabet:
            moved = move(nfa, current, symbol)
            closure = epsilon_closure(nfa, moved)
            if not closure:
                continue
            closure_key = frozenset(closure)
            if closure_key not in state_map:
                state_map[closure_key] = len(dfa_states)
                dfa_states.append(closure)
                stack.append(closure)
                if nfa.final in closure:
                    finals.append(state_map[closure_key])
            dest = state_map[closure_key]
            dfa_transitions[(state_map[current_key], symbol)] = dest
    return DFA(
        initial=0,
        finals=set(finals),
        transitions=dfa_transitions,
        alphabet=alphabet,
        states_count=len(dfa_states),
    )


def are_equivalent(dfa1, dfa2):
    if dfa1.alphabet != dfa2.alphabet:
        return False
    forward = {dfa1.initial: dfa2.initial}
    backward = {dfa2.initial: dfa1.initial}
    stack = [(dfa1.initial, dfa2.initial)]
    visited = set()
    while stack:
        s1, s2 = stack.pop()
        if (s1, s2) in visited:
            continue
        visited.add((s1, s2))
        if (s1 in dfa1.finals) != (s2 in dfa2.finals):
            return False
        for c in dfa1.alphabet:
            t1 = dfa1.transitions.get((s1, c), None)
            t2 = dfa2.transitions.get((s2, c), None)
            if t1 is None and t2 is None:
                continue
            if t1 is None or t2 is None:
                return False
            if t1 in forward:
                if forward[t1] != t2:
                    return False
            else:
                if t2 in backward:
                    if backward[t2] != t1:
                        return False
                else:
                    forward[t1] = t2
                    backward[t2] = t1
            stack.append((t1, t2))
    return True


def regex_to_nfa(regex):
    try:
        tokens = tokenize_regex(regex)
    except ValueError as e:
        raise ValueError(f"Invalid regex: {str(e)}") from e
    postfix = shunting_yard(tokens)
    return build_nfa(postfix)


def main():
    while True:
        regex1 = input("Enter first regex: ")
        regex2 = input("Enter second regex: ")
        nfa1 = regex_to_nfa(regex1)
        nfa2 = regex_to_nfa(regex2)
        dfa1 = nfa_to_dfa(nfa1)
        dfa2 = nfa_to_dfa(nfa2)
        min_dfa1 = dfa1.minimize()
        min_dfa2 = dfa2.minimize()

        print("Equivalent:", are_equivalent(min_dfa1, min_dfa2))
        print("\n")

        while True:
            ans = input("Would you like to enter other data?(y/n)\n")
            if ans == "y" or ans == "n":
                break
            else:
                print("Invalid input")
        if ans == "y":
            continue
        if ans == "n":
            break
    exit = input("Press enter to exit")


if __name__ == "__main__":
    main()
