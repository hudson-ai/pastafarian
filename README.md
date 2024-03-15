# Finite State Machines for [`guidance`](https://github.com/guidance-ai/guidance)
[![Python package](https://github.com/hudson-ai/pastafarian/actions/workflows/tests.yml/badge.svg)](https://github.com/hudson-ai/pastafarian/actions/workflows/tests.yml)

Here's a little re-implementation of `guidance` `regex` grammars using finite state machines (implemented on top of `interegular`). This adds a couple of features that `guidance` does not yet support, including using curly braces to indicate number of occurences, (some) lookaheads, and potentially fixing some issues with negations.

Instead of 
```python
from guidance import regex
```
try
```python
from pastafarian import regex
```

Note that this package depends on some things that are currently not in a released version of `guidance`, including grammars implemented using mutual recursion. So please install `guidance` from source using the most up-to-date version.
