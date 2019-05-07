# -*- coding:Utf-8 -*-


class OrderedSet:
    def __init__(self, iterable=()):
        self._dict = dict()
        for element in iterable:
            self.add(element)

    def add(self, element, move_at_the_end=True):
        if move_at_the_end:
            self._dict.pop(element, None)
        self._dict[element] = None

    def update(self, iterable):
        for element in iterable:
            self.add(element)

    def remove(self, element):
        try:
            self._dict.pop(element)
        except KeyError:
            return
        return element

    def clear(self):
        self._dict.clear()

    def __len__(self):
        return len(self._dict)

    def __contains__(self, item):
        return item in self._dict

    def __iter__(self):
        return iter(self._dict.keys())

    def __repr__(self):
        to_rtn = 'OrderedSet({'
        len_self = len(self)
        if len_self > 50:
            for i, element in enumerate(self):
                if i < 4 or i > len_self - 5:
                    to_rtn += repr(element) + ', '
                elif i == 5:
                    to_rtn += ' ..., '
        else:
            for element in self:
                to_rtn += repr(element) + ', '
        if to_rtn.endswith(', '):
            return to_rtn[:-2] + '})'
        return to_rtn + '})'
