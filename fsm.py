# states as functions. GO
from typing import Callable
from typing_extensions import TypeAliasType
from collections.abc import Mapping, MutableMapping
import interegular

import guidance
from guidance import select
from guidance._grammar import GrammarFunction

State = TypeAliasType("State", int)
Symbol = TypeAliasType("Symbol", int)

@guidance(stateless=True)
def gen_fsm(lm, fsm: interegular.fsm) -> Mapping[State, Callable[[], GrammarFunction]]:
    map: Mapping[State, Mapping[Symbol, State]] = fsm.map
    funcs: Mapping[State, Callable[[], GrammarFunction]] = {}

    def build_func(state: State) -> Callable[[], GrammarFunction]:
        transition: Mapping[Symbol, State] = map[state]

        def closure(lm):
            options = []
            for symbol, state in transition.items():
                # option = symbol
                option = select([k for k,v in fsm.alphabet._symbol_mapping.items() if v == symbol])
                if map[state]:
                    option += funcs[state]()
                options.append(option)
            return lm + select(options)
        closure.__name__ = str(state)

        return guidance(stateless=True, dedent=False)(closure)

    for state in map.keys():
        funcs[state] = build_func(state)

    initial = funcs[fsm.initial]
    return lm + initial()

@guidance(stateless=True)
def gen_regex(lm, pattern):
    fsm = interegular.parse_pattern(pattern).to_fsm()
    return lm + gen_fsm(fsm)

regex = r"[A-Z]{2}"
gen_regex(regex)