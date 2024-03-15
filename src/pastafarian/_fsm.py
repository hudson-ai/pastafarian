from typing import Callable, Any
from collections.abc import Mapping, Collection
from dataclasses import dataclass
import interegular

import guidance
from guidance import select, any_char_but, optional
from guidance._grammar import GrammarFunction

from .util import nice_char_group

# Aliases, purely to make later type annotations readable
State = int
TransitionKey = int

@dataclass
class FSM:
    map: Mapping[State, Mapping[TransitionKey, State]]
    initial: State
    finals: Collection[State]
    grammars: Mapping[TransitionKey, GrammarFunction]

    @classmethod
    def from_interegular_fsm(cls, fsm: interegular.FSM) -> "FSM":
        # Remove redundant states first
        fsm = fsm.reduce()
        alphabet = {
            char
            for char in fsm.alphabet.keys()
            if char != interegular.fsm.anything_else
        }
        grammars = {}
        for transition_key, chars in fsm.alphabet.by_transition.items():
            if interegular.fsm.anything_else in chars:
                assert [interegular.fsm.anything_else] == chars
                grammars[transition_key] = any_char_but(alphabet)
            else:
                grammars[transition_key] = select(nice_char_group(chars))

        return cls(
            map=fsm.map, initial=fsm.initial, finals=fsm.finals, grammars=grammars
        )

    @classmethod
    def from_regex(cls, pattern: str) -> "FSM":
        return cls.from_interegular_fsm(interegular.parse_pattern(pattern).to_fsm())


@guidance(stateless=True)
def fsm(lm, fsm: FSM):
    funcs: Mapping[State, Callable[[], GrammarFunction]] = {}

    def build_func(state: State) -> Callable[[], GrammarFunction]:
        transition: Mapping[TransitionKey, State] = fsm.map[state]

        def closure(lm):
            options = []
            for transition_key, next_state in transition.items():
                option = fsm.grammars[transition_key]
                if fsm.map[next_state]:
                    next_func = funcs.setdefault(next_state, build_func(next_state))
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
