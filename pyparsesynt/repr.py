def _qou(s, mode=1):
    q = "'" if mode == 1 else '"'
    return q + s + q


def _safe_quot(s):
    if s == None:
        return str(s)
    if type(s) == str:
        return _qou(s)
    return str(s)


class ReprBase(object):
    def __repr__(self):
        return self._repr_get()

    def _repr_get(self, bare=False):
        return self._repr_quoted(self._repr_bare(), bare=bare)

    def _repr_bare(self):
        return None

    def _repr_quoted(self, m, bare=False):
        if type(m) == list:
            m = ", ".join([_safe_quot(x) for x in m])
        return ("" if bare else self.__class__.__name__) + "( " + str(m) + " )"
