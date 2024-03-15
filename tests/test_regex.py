import pytest
from guidance._parser import ParserException
from pastafarian import regex


@pytest.mark.parametrize(
    "pattern, string",
    [
        (r'(a|b)c', 'ac'),
        (r'(a|b)c', 'bc'),
        (r'x(?=(a|b))(?=(a|d))', 'xa'),
        (r'(hello){1,3}', 'hello'),
        (r'(hello){1,3}', 'hello'*2),
        (r'(hello){1,3}', 'hello'*3),
    ]
)
def test_match(pattern, string):
    assert regex(pattern).match(string) is not None

@pytest.mark.parametrize(
    "pattern, string, failure_byte",
    [
        (r'(a|b)c', 'dc', b'd'),
        (r'x(?=(a|b))(?=(a|d))', 'xb', b'b'),
        (r'x(?=(a|b))(?=(a|d))', 'xd', b'd'),
        (r'(hello){1,3}', 'hello'*4, b'h'),
    ]
)
def test_failure(pattern, string, failure_byte):
    with pytest.raises(ParserException) as pe:
        regex(pattern).match(string, raise_exceptions=True)
    assert pe.value.current_byte == failure_byte