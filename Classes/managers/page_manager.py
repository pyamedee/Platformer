# -*- coding:Utf-8 -*-

from weakref import WeakValueDictionary


class BasePageManager:

    def __init__(self):
        self.current_page_name = str()
        self.current_page = None
        self.cache = WeakValueDictionary()

    def switch_page(self, page_name, *args, **kwargs):
        if self.current_page is not None:
            self.current_page.deactivate()
            self.cache[self.current_page_name] = self.current_page
            del self.current_page

        if page_name not in self.cache:
            self.current_page = getattr(self, page_name)(*args, **kwargs)
        else:
            self.current_page = self.cache[page_name]
        self.current_page_name = page_name
        self.current_page.activate()

