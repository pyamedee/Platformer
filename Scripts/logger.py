# -*- coding:Utf-8 -*-

import logging as lg
from logging.handlers import RotatingFileHandler


def get_logger():
    _logger = lg.getLogger('main')
    _logger.setLevel(lg.DEBUG)

    formatter = lg.Formatter()

    file_handler = RotatingFileHandler('platformer.log', 'a', 1000000, 1)

    file_handler.setLevel(lg.INFO)
    file_handler.setFormatter(formatter)
    _logger.addHandler(file_handler)

    stream_handler = lg.StreamHandler()

    stream_handler.setLevel(lg.DEBUG)
    stream_handler.setFormatter(formatter)
    _logger.addHandler(stream_handler)

    return _logger


logger = get_logger()
