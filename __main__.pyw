# -*- coding:Utf-8 -*-

import sys

from Model import Model
from Controller import Controller
from Viewer import Viewer
from logger import logger
from pygame.constants import FULLSCREEN
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--debug', action="store_true")
args = parser.parse_args()

DEBUG = args.debug
if not DEBUG:
    DEBUG = True


def main():
    if DEBUG:
        logger.info('Launching Platformer in debug mode')
    else:
        logger.info('Launching Platformer')
    model = Model()
    viewer = Viewer(framerate=30)
    controller = Controller(model, viewer)

    flags = tuple() if DEBUG else (FULLSCREEN,)
    viewer.wdisplay((1280, 720), flags)
    controller.init_pages()
    return viewer.loop()


if __name__ == '__main__':
    sys.exit(main())


