# states as functions. GO
from typing import Callable
from collections.abc import Mapping, Iterable
import interegular

import guidance
from guidance import select, char_range
from guidance._grammar import GrammarFunction

State = int
Symbol = int

def get_byte_ranges(chars: Iterable[str]) -> list[str|bytes]:
    # From interegular.fsm.nice_char_group
    out: list[str|bytes] = []
    current_range: list[str] = []
    for c in sorted(chars):
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

def get_state_bytes(fsm: interegular.fsm.FSM, symbol: Symbol) -> list[bytes]:
    # TODO: handle r'.*' / 'anything else'
    chars = fsm.alphabet._by_transition[symbol]
    return get_byte_ranges(chars)

@guidance(stateless=True)
def gen_fsm(lm, fsm: interegular.fsm.FSM):
    map: Mapping[State, Mapping[Symbol, State]] = fsm.map
    funcs: Mapping[State, Callable[[], GrammarFunction]] = {}

    def build_func(state: State) -> Callable[[], GrammarFunction]:
        transition: Mapping[Symbol, State] = map[state]

        # TODO: handle optional when `state in fsm.finals`

        def closure(lm):
            options = []
            for symbol, next_state in transition.items():
                next_func = funcs.setdefault(next_state, build_func(next_state))
                option = select(get_state_bytes(fsm, symbol))
                if len(map[next_state]) > 0:
                    option += next_func()
                options.append(option)
            return lm + select(options)

        # Set name for repr
        closure.__name__ = str(state)
        closure = guidance(closure, stateless=True, dedent=False)
        return closure

    return lm + build_func(fsm.initial)()

@guidance(stateless=True)
def gen_regex(lm, pattern):
    fsm = interegular.parse_pattern(pattern).to_fsm()
    return lm + gen_fsm(fsm)

regex = r"abcdef[A-Z]"
gen_regex(regex)
