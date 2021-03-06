import collections


dummy = object()


class Item(object):
    __slots__ = ['hash', 'key', 'value']

    def __init__(self):
        self.hash = None
        self.key = None
        self.value = None

    def __repr__(self):
        if self.is_null():
            args = 'null'
        elif self.is_dummy():
            args = 'dummy'
        else:
            args = 'key={}, value={}'.format(self.key, self.value)

        return '<Item({})>'.format(args)

    def is_null(self):
        return self.hash is None

    def is_dummy(self):
        return self.hash is dummy

    def is_set(self):
        return not (self.is_null() or self.is_dummy())

    def set(self, h, key, value):
        self.hash = h
        self.key = key
        self.value = value

    def unset(self):
        self.hash = dummy
        self.key = None
        self.value = None

    def equals(self, h, key):
        return self.hash == h and self.key == key


class pydict(collections.MutableMapping):
    def __init__(self):
        self._resize(8)

    def _resize(self, n):
        self._used = 0
        self._remaining = int(n * 2.0 / 3)
        self._size = n
        self._mask = n - 1
        self._table = [Item() for _ in xrange(n)]

    def _find(self, h, key):
        i = h & self._mask
        item = self._table[i]

        if item.is_null() or item.equals(h, key):
            return item
        elif item.is_dummy():
            free = item
        else:
            free = None

        perturb = h

        while True:
            i = i * 5 + perturb + 1
            item = self._table[i & self._mask]

            if item.is_null():
                if free is not None:
                    return free
                else:
                    return item
            elif item.equals(h, key):
                return item
            elif item.is_dummy() and free is None:
                free = item

            perturb >>= 5

    def __len__(self):
        return self._used

    def __getitem__(self, key):
        item = self._find(hash(key), key)

        if item.is_set():
            return item.value
        else:
            raise KeyError(key)

    def __setitem__(self, key, value):
        if self._remaining == 0:
            items = list(self.items())
            self._resize(self._size * 2)

            for key, value in items:
                self.__setitem__(key, value)

        h = hash(key)
        item = self._find(h, key)

        if not item.is_set():
            self._used += 1
            self._remaining -= 1

        item.set(h, key, value)

    def __delitem__(self, key):
        item = self._find(hash(key), key)

        if item.is_set():
            item.unset()
            self._used -= 1
            self._remaining += 1
        else:
            raise KeyError(key)

    def __iter__(self):
        for item in self._table:
            if item.is_set():
                yield item.key
