# -*- coding:Utf-8 -*-


class BaseEventManager:

    prefix = 'hdlr'

    def __init__(self, action_handler):
        self.action_handler = action_handler
        self.handlers = {}

    def get_handlers(self):
        if not self.handlers:
            for func_name in dir(self):
                if func_name.startswith(self.prefix):
                    self.handlers['on' + func_name[len(self.prefix):]] = getattr(self, func_name)
        return self.handlers
