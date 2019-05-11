# -*- coding:Utf-8 -*-

import argparse
import sys

from pygame.constants import FULLSCREEN

from Classes.controller import Controller
from Classes.model import Model
from Classes.viewer import Viewer
from Scripts.configurations import general_cfg
from Scripts.logger import logger

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action="store_true")
args = parser.parse_args()

DEBUG = args.debug
if not DEBUG:
    DEBUG = general_cfg.getboolean('debug_mode')


def main():
    if DEBUG:
        logger.info('Launching Platformer in debug mode')
    else:
        logger.info('Launching Platformer')
    model = Model()
    viewer = Viewer(model.get_text, framerate=60)
    controller = Controller(model, viewer)

    flags = tuple() if DEBUG else (FULLSCREEN,)
    viewer.wdisplay((general_cfg.getint('resolution_x'),
                    general_cfg.getint('resolution_y')),
                    flags)
    controller.init_pages()
    return viewer.loop()


if __name__ == '__main__':
    sys.exit(main())
