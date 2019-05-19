# -*- coding:Utf-8 -*-


class PageManager:

    def __init__(self):
        self.current_page = None

    def add_page(self, page_name, *args, **kwargs):
        self.current_page = getattr(self, page_name)(*args, **kwargs)
        self.current_page.activate()

    def switch_page(self, page_name, *args, **kwargs):
        if self.current_page is None:
            raise RuntimeError('Please add a page with the "add_page" method before switching to another page.')
        self.current_page.deactivate()
        del self.current_page

        self.current_page = getattr(self, page_name)(*args, **kwargs)
        self.current_page.activate()
