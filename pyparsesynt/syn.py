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
            rc = (" ") * (ident - 1) + "-" + str(sub._head) + "\n"

        offs = 1 if sub._head else 0

        for t in sub._tail:
            if t == None or len(t) == 0:
                continue
            if type(t) == Element:
                rc += self.__as_str__(t, ident + offs)
            else:
                rc += " " * (ident + offs - 1) + "-" + str(t) + "\n"

        return rc

    def head(self, elem):
        self._head = elem
        return self

    def get_head(self):
        return self._head

    def get_tail(self):
        return self._tail

    def add(self, elem):
        self._tail.append(elem)
        return self

    def __len__(self):
        cnt = len(self._tail)
        if self._head:
            cnt += 1
        return cnt
