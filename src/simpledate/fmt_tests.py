
from unittest import TestCase
from re import compile
from simpledate.fmt import _to_regexp, reconstruct


class RegexpTest(TestCase):

    def test_marker(self):
        # shows we can use an empty pattern to mark which option is matched
        rx = compile(r'(?P<a1>)x')
        m = rx.match('x')
        assert m, 'no match'
        assert 'a1' in m.groupdict(), m.groupdict()
        assert m.groupdict()['a1'] is not None, m.groupdict()['a1']
        rx = compile(r'((?P<a>)a|b)')
        m = rx.match('a')
        assert m, 'no match'
        assert 'a' in m.groupdict(), m.groupdict()
        assert m.groupdict()['a'] is not None, m.groupdict()['a']
        m = rx.match('b')
        assert m, 'no match'
        assert 'a' in m.groupdict(), m.groupdict()
        assert m.groupdict()['a'] is None, m.groupdict()['a']
        rx = compile(r'((?P<a>)a|(?P<b>)b)')
        m = rx.match('b')
        assert m, 'no match'
        assert 'a' in m.groupdict(), m.groupdict()
        assert m.groupdict()['a'] is None, m.groupdict()['a']
        assert 'b' in m.groupdict(), m.groupdict()
        assert m.groupdict()['b'] is not None, m.groupdict()['b']


class ParserTest(TestCase):

    def assert_regexp(self, target, expr, subs):
        result, _, _ = _to_regexp(expr, subs)
        assert target == result, result

    def test_regexp(self):
        self.assert_regexp('abc', 'abc', {})
        self.assert_regexp('abXc', 'ab%xc', {'%x': 'X'})
        self.assert_regexp('ab((?P<G1>)X)c', 'ab{%x}c', {'%x': 'X'})
        self.assert_regexp('a((?P<G1>)b)?c', 'ab?c', {})

    def test_subs(self):
        self.assert_regexp(r'(?P<Y>\d\d\d\d)-(?P<m>1[0-2]|0[1-9]|[1-9])-(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9])', '%Y-%m-%d', None)
        self.assert_regexp(r'((?P<G1>)(?P<d>3[0-1]|[1-2]\d|0[1-9]|[1-9]| [1-9]))?', '%d?', None)

    def assert_parser(self, target_regexp, target_rebuild, expr, subs):
        regexp, rebuild, _ = _to_regexp(expr, subs)
        assert target_regexp == regexp, regexp
        assert target_rebuild == rebuild, rebuild

    def test_parser(self):
        self.assert_parser('abc', {'G0': 'abc'}, 'abc', {})
        self.assert_parser('abC', {'G0': 'abc'}, 'abc!', {'c!': 'C'})
        self.assert_parser('ab((?P<G1>)xyz)c', {'G0': 'ab%G1%c', 'G1': 'xyz'}, 'ab{xyz}c', {})
        self.assert_parser('ab((?P<G1>)xy|(?P<G2>)z)c', {'G0': 'ab%G1%%G2%c', 'G1': 'xy', 'G2': 'z'}, 'ab{xy|z}c', {})
        self.assert_parser('ab((?P<G1>)c)?', {'G0': 'ab%G1%', 'G1': 'c'}, 'abc?', {})
        self.assert_parser('ab((?P<G1>)((?P<G2>)c)?|(?P<G3>)de((?P<G4>)X)?)', {'G0': 'ab%G1%%G3%', 'G1': '%G2%', 'G2': 'c', 'G3': 'de%G4%', 'G4': '%x'}, 'ab{c?|de%x?}', {'%x': 'X'})

    def assert_reconstruct(self, target, expr, text):
        pattern, rebuild, regexp = _to_regexp(expr)
        match = regexp.match(text)
        result = reconstruct(rebuild, match.groupdict())
        assert result == target, result

    def test_reconstruct(self):
        self.assert_reconstruct('ab', 'a{b|c}d?', 'ab')
        self.assert_reconstruct('ac', 'a{b|c}d?', 'ac')
        self.assert_reconstruct('abd', 'a{b|c}d?', 'abd')
        self.assert_reconstruct('%S', '{{%H:}?%M:}?%S', '56')
        self.assert_reconstruct('ab', 'a ?b', 'ab')
        self.assert_reconstruct('a b', 'a ?b', 'a b')
