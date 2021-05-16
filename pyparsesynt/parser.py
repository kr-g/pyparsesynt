from pyparsesynt.token import Token, TokenStream, BackPos
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
from .repr import ReprBase
from .syn import Element


class NoSolution(Exception):
    pass


class LexerTokens(object):
    def __init__(self, tok):
        self.tok = tok
        self.__dict__.update(zip(tok.map.keys(), tok.map.keys()))


class Parser(ReprBase):
    def __init__(self, debug=False):
        self._debug = debug
        self.rules = {}
        self.ts = None
        self.root = Element()

    def __repr__(self):
        res = ""
        for prod, rules in self.rules.items():
            res += "".join([prod + " ::=\t" + str(i.mat) for i in rules])
            res += "\n\r"
        return res

    def extend(self, prods):
        for p in prods:
            self.append(p)

    def append(self, prod):
        prod.parser = self
        prod_alt = self.rules.setdefault(prod.name, [])
        prod_alt.append(prod)

    def Production(self, name, mat, alias=None, auto_add=True):
        prod = Production(name, mat, parser=self, alias=alias)
        if auto_add == True:
            self.append(prod)
        return prod

    def Call(self, target):
        return Call(target, parser=self)

    def set_input(self, tokens):
        tokens = list(tokens)
        self.ts = TokenStream(tokens)

    def _get_subset(self, tar):
        return self.rules.get(tar)

    def _run_valid(self, tar, it, root):
        prod_alt = self._get_subset(tar)
        found_alt = self._run_set(tar, prod_alt, self.ts)
        return self._run_invoke(found_alt, root=root)

    def _run_set(self, tar, subset, it):
        found = []
        pos = BackPos(it)
        for alt in subset:
            rc = alt.valid(it)
            if rc:
                found.append((alt, BackPos(it), alt.elem))
            pos.revert()
        return found

    def _run_invoke(self, found, root):

        if len(found) > 0:
            fp = max(found, key=lambda x: x[1])
            prod, pos, elem = fp
            pos.revert()
            # elem = self._invoke_resolve(prod, lastpos)
            if root != None:
                if elem != None:
                    root.add(elem)
            return True, fp

    def run(self):
        root = Element("---root---")
        while len(self.ts) > 0:
            last = BackPos(self.ts)
            found = []
            self._debug and print("---round start", self.ts.peek())
            for tar in self.rules.keys():
                elem = Element()
                rc = self._run_valid(tar, self.ts, root=elem)
                if rc:
                    _, (prod, pos, elem) = rc
                    found.append((prod, pos, elem))
                last.revert()

            self._debug and print("---round result", self.ts.peek())
            if len(found) == 0:
                raise NoSolution()

            self._debug and print(found)

            fp = max(found, key=lambda x: x[1])
            prod, pos, elem = fp
            root.add(elem)
            pos.revert()

            self._debug and print("---round done")
            self._debug and print()

        return root
