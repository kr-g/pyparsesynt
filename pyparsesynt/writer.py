import sys

from pyparsesynt.rule import (
    Production,
    Call,
    Terminal,
    And,
    Or,
    Not,
    Optional,
    Repeat,
)


def _qou(s):
    return "'" + s + "'"


class Writer(object):
    def write(self, prod_rules, file=None):
        if file == None:
            file = sys.stdout
        for _, mats in prod_rules.items():
            for prod in mats:
                outs = self._str_term(prod)
                print(outs, file=file)

    def _str_term(self, match, enclose=True):

        ttyp = type(match)

        if ttyp == Production:
            return match.name + " ::= " + self._str_term(match.mat)

        elif ttyp == Call:
            return match.prod

        elif ttyp == Terminal:
            return _qou(match.val) if match.val else match.typ

        elif ttyp == Or:
            return " | ".join([self._str_term(x) for x in match.rules])

        elif ttyp == And:
            return "(" + ", ".join([self._str_term(x) for x in match.rules]) + ")"

        elif ttyp == Optional:
            return "[" + self._str_term(match.rule) + "]"

        elif ttyp == Repeat:
            r = None
            if match._min == 0 and match._max == None:
                r = "*"
            elif match._min == 0 and match._max == 1:
                r = "?"
            elif match._min == 1 and match._max == None:
                r = "+"
            else:
                r = f"({match._min}, {match._max})"
            return "{" + self._str_term(match.rule) + "}" + r

        else:
            raise Exception("unexpected", match)

        return str(match)
