# -*- coding:Utf-8 -*-


class BaseActionManager:
    def __call__(self, action_type, action_name):
        if action_name:
            return getattr(self, action_type + '_' + action_name)()
