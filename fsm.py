# states as functions. GO
from typing import Callable, Union
from collections.abc import Mapping, Iterable
from interegular import parse_pattern
from interegular.fsm import FSM, anything_else, _AnythingElseCls

import guidance
from guidance import select, char_range, any_char_but, optional
from guidance._grammar import GrammarFunction

State = int
Symbol = int

def get_byte_ranges(chars: Iterable[Union[str, _AnythingElseCls]], alphabet: Iterable[str]):
    # From interegular.fsm.nice_char_group
    out: list[str|bytes] = []
    current_range: list[str] = []
    for c in sorted(chars):
        if c is anything_else:
            out.append(any_char_but(alphabet))
            continue
        assert not isinstance(c, _AnythingElseCls)
        if current_range and ord(current_range[-1]) + 1 == ord(c):
            current_range.append(c)
            continue
        if len(current_range) >= 2:
            out.append(char_range(current_range[0], current_range[-1]))
        else:
            out.extend(current_range)
        current_range = [c]
    if len(current_range) >= 2:
        out.append(char_range(current_range[0], current_range[-1]))
    else:
        out.extend(current_range)
    return out

def get_choices(fsm: FSM, symbol: Symbol):
    chars = fsm.alphabet._by_transition[symbol]
    return get_byte_ranges(chars, [char for char in fsm.alphabet if char is not anything_else])

@guidance(stateless=True)
def gen_fsm(lm, fsm: FSM):
    map: Mapping[State, Mapping[Symbol, State]] = fsm.map
    funcs: Mapping[State, Callable[[], GrammarFunction]] = {}

    def build_func(state: State) -> Callable[[], GrammarFunction]:
        transition: Mapping[Symbol, State] = map[state]

        def closure(lm):
            options = []
            for symbol, next_state in transition.items():
                next_func = funcs.setdefault(next_state, build_func(next_state))
                option = select(get_choices(fsm, symbol))
                if len(map[next_state]) > 0:
                    option += next_func()
                options.append(option)
            if state in fsm.finals:
                return lm + optional(select(options))
            return lm + select(options)

        # Set name for repr
        closure.__name__ = str(state)
        closure = guidance(closure, stateless=True, dedent=False)
        return closure

    return lm + build_func(fsm.initial)()

@guidance(stateless=True)
def gen_regex(lm, pattern):
    fsm = parse_pattern(pattern).to_fsm()
    return lm + gen_fsm(fsm)
