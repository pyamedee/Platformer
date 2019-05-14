# -*- coding:Utf-8 -*-


class BaseEventHandler:
    def __init__(self, viewer_page, action_handler):
        self.action_handler = action_handler
        self.viewer_page = viewer_page


class BaseActionHandler:
    def __call__(self, action_type, action_name):
        if action_name:
            return getattr(self, action_type + '_' + action_name)()

