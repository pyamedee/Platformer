# -*- coding:Utf-8 -*-

from collections import deque
from .exceptions import Full, Empty


class BaseQueue:
    def __init__(self, d=()):
        self._queue = self.init_queue(d)

    def __repr__(self):
        return self.not_formatted_repr().format('')

    def not_formatted_repr(self):
        return '([' + ', '.join((repr(a) for a in self._queue)) + ']{})'

    def __iter__(self):
        return iter(self._queue)

    def __len__(self):
        return len(self._queue)

    @staticmethod
    def init_queue(d):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def put(self, element):
        self._queue.append(element)

    def pump(self):
        self._queue.clear()

    def elements(self):
        return QueueIterator(self)

    def update(self, d):
        self._queue += d


class QueueIterator:
    def __init__(self, queue):
        self.queue = queue

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.queue.get()
        except Empty:
            raise StopIteration


class MaxSize(BaseQueue):
    def __init__(self, maxsize, d=()):
        if len(d) > maxsize:
            raise Full
        super(MaxSize, self).__init__(d)
        if not isinstance(self, BaseQueue):
            raise TypeError('self must be an instance of a subclass of BaseQueue')
        self.maxsize = maxsize

    def put(self, element):
        if len(self) + 1 > self.maxsize:
            raise Full
        super().put(element)

    def update(self, d):
        if len(self) + len(d) > self.maxsize:
            raise Full
        super().update(d)

    def __repr__(self):
        return super().not_formatted_repr().format(', maxsize={}'.format(self.maxsize))


class DequeQueue(BaseQueue):
    def not_formatted_repr(self):
        return 'deque_queue' + super().not_formatted_repr()

    @staticmethod
    def init_queue(d):
        if isinstance(d, deque):
            return d
        return deque(d)

    def get(self):
        try:
            return self._queue.popleft()
        except IndexError:
            pass
        raise Empty

    def to_deque(self, copy=True):
        if copy:
            return self._queue.copy()
        return self._queue


class StackQueue(BaseQueue):
    def not_formatted_repr(self):
        return 'stack_queue' + super().not_formatted_repr()

    @staticmethod
    def init_queue(d):
        if isinstance(d, list):
            return d
        return list(d)

    def get(self):
        try:
            return self._queue.pop()
        except IndexError:
            pass
        raise Empty

    def to_list(self, copy=True):
        if copy:
            return self._queue.copy()
        return self._queue


class MaxsizeDequeQueue(MaxSize, DequeQueue):
    pass


class MaxsizeStackQueue(MaxSize, StackQueue):
    pass


if __name__ == '__main__':
    print(0)
