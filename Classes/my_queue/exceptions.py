# -*- coding:Utf-8 -*-

class Full(Exception):
    def __str__(self):
        return 'Full'


class Empty(Exception):
    def __str__(self):
        return 'Empty'
