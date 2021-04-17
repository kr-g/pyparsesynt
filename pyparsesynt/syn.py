from .repr import ReprBase


class Element(ReprBase):
    def __init__(self, head=None):
        self.reset(head)

    def reset(self, head=None):
        self._head = head
        self._tail = []
        self._maxpos = None

    def _repr_bare(self):
        return [self._head, self._tail]

    def __repr__(self):
        return self.__as_str__(self)

    def __as_str__(self, sub, ident=1):

        rc = ""
        if sub._head:
            rc = ("-" if ident == 1 else " ") * (ident - 1) + "-" + sub._head + "\n"

        for t in sub._tail:
            if t == None or len(t) == 0:
                continue
            if type(t) == Element:
                rc += self.__as_str__(t, ident + 1)
            else:
                rc += " " * ident + "+" + str(t)
                rc += "\n"

        return rc

    def head(self, elem):
        self._head = elem
        return self

    def add(self, elem):
        self._tail.append(elem)
        return self

    def __len__(self):
        cnt = len(self._tail)
        if self._head:
            cnt += 1
        return cnt
