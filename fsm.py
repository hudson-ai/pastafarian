# states as functions. GO
from typing import Callable
from typing_extensions import TypeAliasType
from collections.abc import Mapping, MutableMapping
import interegular

import guidance
from guidance import select, byte_range
from guidance._grammar import GrammarFunction

State = TypeAliasType("State", int)
Symbol = TypeAliasType("Symbol", int)

def get_state_bytes(fsm: interegular.fsm, symbol: Symbol) -> list[str]:
    chars = fsm.alphabet._by_transition[symbol]
    if len(chars) == 1:
        return chars
    bts = sorted([bytes(char, encoding='utf8') for char in chars])
    ints = [int.from_bytes(b) for b in bts]
    if ints == list(range(ints[0], ints[0]+len(ints))):
        return [byte_range(bts[0], bts[-1])]
    return bts

@guidance(stateless=True)
def gen_fsm(lm, fsm: interegular.fsm):
    map: Mapping[State, Mapping[Symbol, State]] = fsm.map
    funcs: Mapping[State, Callable[[], GrammarFunction]] = {}

    def build_func(state: State) -> Callable[[], GrammarFunction]:
        transition: Mapping[Symbol, State] = map[state]

        def closure(lm):
            options = []
            for symbol, state in transition.items():
                option = select(get_state_bytes(fsm, symbol))
                if state not in fsm.finals:
                    option += funcs.setdefault(state, build_func(state))()
                options.append(option)
            return lm + select(options)
        closure.__name__ = str(state)

        return guidance(stateless=True, dedent=False)(closure)

    return lm + build_func(fsm.initial)()

@guidance(stateless=True)
def gen_regex(lm, pattern):
    fsm = interegular.parse_pattern(pattern).to_fsm()
    return lm + gen_fsm(fsm)

regex = r"abcdef(g|h)"
gen_regex(regex)
