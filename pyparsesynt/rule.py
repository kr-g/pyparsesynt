from .token import Token, BackPos
from .repr import ReprBase
from .syn import Element


class Match(ReprBase):
    def __init__(self):
        ReprBase.__init__(self)
        self.elem = Element()

    def valid(self, it):

        last = BackPos(it)

        self.elem = Element()

        rc = self._valid_build_from(it, last)

        if not True:
            if rc == True or self._parent == None:
                p = it.peek()
                if self._parent:
                    print(self._parent.name, end=" <- ")
                print(str(self), "==peek==", p, end="")
                print(*("", "=>", rc) if (rc or self._parent == None) else "")
                if self._parent == None:
                    print()

        return rc

    def _valid_build_from(self, it, last):
        rc = self._valid(it)
        if rc:
            self.build_from(last)
        return rc

    def _valid(self, it):
        raise NotImplementedError()

    def build_from(self, last_it):
        # self._build_from(self.elem,last_it)
        return self.elem

    def _build_from(self, elem, last_it):
        self._build_from_head(elem, last_it)
        self._build_from_tail(elem, last_it)

    def _build_from_head(self, elem, last_it):
        if self._parent == None:
            elem.head(self.alias if self.alias else self.name)

    def _build_from_tail(self, elem, last_it):
        val = last_it.capture()
        if len(val) == 1:
            val = val[0]
        elem.add(val)

    def parent(self, parent=None):
        self._parent = parent
        return self
        if parent:
            print(self.__class__.__name__, parent.name)


# Production should be created via Parser


class Production(Match):
    def __init__(self, name, match, parser, alias=None):
        super().__init__()
        self.name = name
        self.alias = alias
        self.mat = match
        self.parser = parser
        self.parent()
        self.mat.parent(self)

        if self.name:
            if len(self.name) == 0:
                raise Exception("empty")
            if not (self.name.islower() and self.name.isascii()):
                raise Exception("type not normalized")

    def _valid(self, it):
        return self.mat.valid(it)

    def build_from(self, last_it):
        self.elem = self.mat.elem
        self.elem.head(self.alias if self.alias else self.name)
        return self.elem

    def __repr__(self):
        return self._repr_quoted([self.name, self.mat])


# Call should be created via Parser


class Call(Match):
    def __init__(self, prod, parser):
        super().__init__()
        if type(prod) == Production:
            prod = prod.name
        self.prod = prod
        self.parser = parser

    def _valid(self, it):

        recur = self._parent.name == self.prod

        if recur:
            cnt = it.recur(self.prod)
            if cnt >= 1:
                raise Exception("recursion", cnt)

        rc = self.parser._run_valid(self.prod, it, root=self.elem)
        if rc:
            rc, _ = rc

        if recur:
            it.recur(self.prod, leave=True)

        return rc

    def build_from(self, last_it):
        return self.elem

    def __repr__(self):
        return self._repr_quoted(self.prod)


#


class Terminal(Match):
    def __init__(self, val=None, typ=None):
        Match.__init__(self)
        self.val = val
        self.typ = typ
        self.token = Token(val, typ)

        if self.typ:
            if len(self.typ) == 0:
                raise Exception("empty")
            if not (self.typ.isupper() and self.typ.isascii()):
                raise Exception("type not normalized")

    def __repr__(self):
        return self._repr_quoted(self.token)

    def _valid(self, it):
        pek = it.peek()
        if pek == None:
            return False
        if pek == self.token:
            it.pop()
            return True

    def build_from(self, last_it):
        self._build_from(self.elem, last_it)
        return self.elem


class ManyRuleBase(Match):
    def __init__(self, rules):
        super().__init__()
        self.rules = rules

    def __repr__(self):
        return self._repr_quoted(self.rules)

    def parent(self, parent=None):
        super().parent(parent)
        for r in self.rules:
            r.parent(parent)


class And(ManyRuleBase):
    def _valid(self, it):
        pos = BackPos(it)
        for r in self.rules:
            rc = r.valid(it)
            # print("AND",rc,it)
            if rc != True:
                pos.revert()
                return False
            # self.elem.head("***AND")
            self.elem.add(r.elem)
        return True


class Or(ManyRuleBase):
    def _valid(self, it):
        pos = BackPos(it)
        found = []
        for r in self.rules:
            rc = r.valid(it)
            # print("OR",rc,it)
            if rc == True:
                # print("OR->",rc,r)
                found.append((r, BackPos(it), r.elem))
                pos.revert()

        if len(found) > 0:
            self.rc_found = max(found, key=lambda x: x[1])
            rule, foundpos, elem = self.rc_found
            # print("OR pos",foundpos)
            foundpos.revert()
            self.elem = elem
            return True

        pos.revert()


class SingleRuleBase(Match):
    def __init__(self, rule):
        super().__init__()
        self.rule = rule

    def __repr__(self):
        return self._repr_quoted(self.rule)

    def _valid(self, it):
        return self.rule.valid(it)

    def build_from(self, last_it):
        self.elem = self.rule.elem

    def parent(self, parent=None):
        super().parent(parent)
        self.rule.parent(parent)


class Optional(SingleRuleBase):
    def _valid(self, it):
        pos = BackPos(it)
        rc = SingleRuleBase._valid(self, it)
        if rc == False:
            pos.revert()
        return True

    def build_from(self, last_it):
        self.elem = self.rule.elem


class Repeat(SingleRuleBase):
    def __init__(self, rule, min_val=0, max_val=None, name=None):
        super().__init__(rule)
        self._min = min_val
        self._max = max_val
        self._name = name

    def _in_range(self, cnt):
        if cnt >= self._min:
            if self._max != None:
                return cnt < self._max
            return True
        return False

    def _valid(self, it):
        cnt = 0
        pos = None
        self.elem_hier = Element()

        while True:
            rc = super()._valid(it)
            if rc:

                self.elem_hier.add(self.rule.elem)

                pos = BackPos(it)
                cnt += 1
                # todo elem

            if not rc:
                if self._in_range(cnt):
                    if pos:
                        pos.revert()
                    return True
                return False

            if self._max != None and cnt >= self._max:
                if pos:
                    pos.revert()
                    return True
                return False

    def build_from(self, last_it):
        self.elem = self.elem_hier
        nam = "*"
        if self._name:
            nam += self._name
        else:
            if type(self.rule) == Call:
                nam += self.rule.prod
        self.elem.head(nam)


class Not(SingleRuleBase):
    def valid(self, it):

        raise Exception("not used,  nor tested")

        rc = super().valid(it)
        if not rc:
            it.pop()
            return True


#
