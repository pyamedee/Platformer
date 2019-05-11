# -*- coding:Utf-8 -*-

from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('data\\config.ini')

general_cfg = cfg['General configuration']
sp_cfg = cfg['Starting page configuration']
