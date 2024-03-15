import guidance
from ._fsm import FSM, fsm

@guidance(stateless=True)
def regex(lm, pattern: str):
    return lm + fsm(FSM.from_regex(pattern))
