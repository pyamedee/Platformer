# -*- coding:Utf-8 -*-

import traceback as tb
import logging as lg


def create_loggers():
    main_logger = lg.getLogger(__name__)
    main_logger.setLevel(lg.DEBUG)
    file_handler = lg.FileHandler('main.log')
    stream_handler = lg.StreamHandler()

    error_logger = lg.getLogger(__name__ + '.error')
    error_logger.setLevel(lg.ERROR)
    error_handler = lg.FileHandler('main.error.log')

    fmt_main = lg.Formatter('%(asctime)s | %(levelname)s | line %(lineno)s | %(message)s')
    fmt_error = lg.Formatter('{:-^20}\nat %(asctime)s:\n %(exc_tb)s'.format('%(levelname)s'))

    file_handler.setFormatter(fmt_main)
    file_handler.setLevel(lg.INFO)
    stream_handler.setFormatter(fmt_main)
    stream_handler.setLevel(lg.DEBUG)

    error_handler.setFormatter(fmt_error)

    main_logger.addHandler(file_handler)
    main_logger.addHandler(stream_handler)

    error_logger.addHandler(error_logger)


class ExceptionWrapper:
    def __init__(self, logger):
        self.logger = logger

    def __enter__(self):
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            if getattr(exc_val, 'handled', False):
                self.logger.info('An exception occurred and was handled.')
            else:
                self.logger.warning('An exception occurred and has not been handled yet.')
                self.logger.error(exc_val, extra={'exc_tb': ''.join(tb.format_exception(exc_type, exc_val, exc_tb))})
                return False


if __name__ == '__main__':
    create_loggers()
    with ExceptionWrapper(lg.getLogger('__main__.error')):
        passu
