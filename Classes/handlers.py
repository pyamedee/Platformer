# -*- coding:Utf-8 -*-


class BaseEventHandler:
    def __init__(self, viewer_page, action_handler):
        self.action_handler = action_handler
        self.viewer_page = viewer_page


class BaseActionHandler:
    def __call__(self, name, stop=False):
        if not stop:
            return getattr(self, 'do_' + name)()
        getattr(self, 'stop_' + name)()

    def __getitem__(self, item, stop=False):
        if not stop:
            return getattr(self, 'do_' + name)
        return getattr(self, 'stop_' + name)
