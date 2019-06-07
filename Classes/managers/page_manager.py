# -*- coding:Utf-8 -*-

from weakref import WeakValueDictionary
from Scripts.logger import logger


class BasePageManager:

    def __init__(self):
        self.current_page_name = str()
        self.current_page = None
        self.cache = dict()

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

    def clear_cache(self):
        for key in self.cache.copy():
            if hasattr(self.cache[key], 'delete'):
                self.cache[key].delete()
            del self.cache[key]
        logger.debug('cache cleared')
