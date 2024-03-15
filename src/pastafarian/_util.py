from typing import List, Any
from collections.abc import Iterable
from guidance import char_range

def nice_char_group(chars: Iterable[str]) -> List[Any]:
    """
    Condenses a list of characters to a list of "nice" guidance byte ranges,
    e.g. ['A','B','C','D','1','2','3'] -> [b'AB', b'13']

    Code adapted from interegular.fsm.nice_char_group
    """ 
    out = []
    current_range = []
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
