# -*- coding:Utf-8 -*-

import traceback


class ExceptionWrapper:
    def __init__(self, logger):
        self.logger = logger

    def __enter__(self):
        return

    def __exit__(self, etype, value, tb):
        if etype == SystemExit:
            return False
        if getattr(value, 'handled', False):
            self.logger.info('an error occurred and was handled')
        elif etype:
            self.logger.warning('an error occurred and has not been handled yet')
            a = ''.join(traceback.format_exception(etype, value, tb))
            self.logger.critical(value, extra={'traceback': a})
        else:
            logger.info('program ran normally')
        return False
