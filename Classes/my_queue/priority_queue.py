# -*- coding:Utf-8 -*-

import time
import numpy as np
from .exceptions import Full, Empty
import code


def timeit(func, loop):
    times = list()
    tt1 = time.process_time()
    for _ in range(loop):
        t1 = time.perf_counter()
        func()
        times.append(time.perf_counter() - t1)
    tt2 = time.process_time()

    mint, maxt = min(times), max(times)
    mean = sum(times) / len(times)
    tt = tt2 - tt1
    print(f'''min : {mint}, max : {maxt},
'mean : {mean}, total time : {tt}''')


class PriorityQueue:
    def __init__(self, size):
        self.array = np.zeros(size, dtype=np.uint16) + 65535
        self.d = {}
        self.end = -1
        self.issorted = True

    def sort(self):
        self.array.sort()
        self.issorted = True
    
    def _get(self):
        value = self.array[self.end]
        self.array[self.end] = 65535
        self.end -= 1
        return self.d.pop(value)

    def get(self):
        if self.end < 0:
            raise Empty
        elif not self.issorted:
            self.sort()
        return self._get()

    def _put(self, priority, value):
        self.end += 1
        while priority in self.d:
            priority -= 1
        if not isinstance(priority, int):
            raise ValueError('priority must be int')
        self.array[self.end] = priority
        self.d[priority] = value

    def put(self, priority, value, sort=True):
        if self.end + 1 >= self.array.shape[0]:
            raise Full
        self._put(priority, value)
        if sort:
            self.sort()
        else:
            self.issorted = False

    def update(self, d):
        if self.end + len(d) >= self.array.shape[0]:
            raise Full
        for key, value in d.items():
            self._put(key, value)
        self.sort()

    def get_all(self):
        return PriorityQueueIterator(self)

    def __len__(self):
        return self.array.shape[0]

    def __repr__(self):
        sorted_d = sorted(self.d)
        return 'priority_queue(' + repr({l: self.d[l] for l in sorted_d}) + ')'


class PriorityQueueIterator:
    def __init__(self, queue):
        if not queue.issorted:
            queue.sort()

        self.d = queue.d.copy()
        self.array = queue.array[:queue.end + 1].copy()
        self.i = queue.end

        queue.array[:] = 65535
        queue.end = -1
        queue.d.clear()

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < 0:
            raise StopIteration
        value = self.d[self.array[self.i]]
        self.i -= 1
        return value


