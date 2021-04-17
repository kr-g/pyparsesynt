from .repr import ReprBase


class Token(ReprBase):
    def __init__(self, val, typ=None):
        self.val = val
        self.typ = typ

    def _repr_bare(self):
        return [self.val, self.typ]

    def __eq__(self, other):
        if other == None:
            return False
        if self.typ:
            if other.typ:
                if self.typ != other.typ:
                    return False
        if self.val:
            if other.val:
                if self.val != other.val:
                    return False
        return True


class BackPos(ReprBase):
    def __init__(self, ts):
        self.ts = ts
        self.pos = ts.pos()

    def __repr__(self):
        return self._repr_quoted(self.pos)

    def __eq__(self, other):
        return other != None and self.pos == other.pos

    def __lt__(self, other):
        if self.pos is None:
            return True
        if other.pos is None:
            return False
        return self.pos < other.pos

    def revert(self):
        self.ts.reset(self.pos)

    def capture(self):
        return self.ts.capture(self.pos)

    def diff(self, other):
        return self.pos - other.pos


class TokenStream(ReprBase):
    def __init__(self, tokens, pos=0):
        self._tokens = tokens
        self._pos = pos
        self._recur = {}

    def clone(self):
        return TokenStream(self._tokens, self._pos)

    def __repr__(self):
        return self._repr_quoted(self._tokens[self._pos :])

    def _has_more(self):
        return self._pos < len(self._tokens)

    def capture(self, pos):
        return self._tokens[pos : self._pos]

    def pop(self):
        tok = self.peek()
        if tok != None:
            self._pos += 1
            # print("pop >>", tok)
            return tok

    def peek(self):
        if not self._has_more():
            return None
        val, typ = self._tokens[self._pos]
        return Token(val, typ)

    def pushb(self):
        self._pos -= 1
        if self._pos < 0:
            raise Exception("underflow")

    def reset(self, pos=0):
        if pos < 0 or pos > len(self._tokens):
            raise Exception("index", pos)
        self._pos = pos

    def pos(self):
        return self._pos

    def __len__(self):
        return len(self._tokens) - self._pos

    def __iter__(self):
        while self._has_more():
            yield self.pop()

    def recur(self, prod, leave=False):
        cnt = self._recur.setdefault(prod, 0)
        cnt = cnt - 1 if leave else cnt + 1
        self._recur[prod] = cnt
        return cnt
