# -*- coding:Utf-8 -*-

import sys
import os
from configparser import ConfigParser
import sqlite3

available_languages_ = {}
base_ = os.environ.get('BASE')


def setup():
    database = sqlite3.connect(f'{base_}\\data\\data.db')

    cursor = database.execute('SELECT long_name, short_name FROM AvailableLanguages')
    data = tuple(cursor)
    for long_name, short_name in data:
        available_languages_[short_name] = long_name
    database.close()


def main(base, available_languages):
    cfg = ConfigParser()

    with open(f'{base}\\data\\config.ini', 'r') as file:
        txt = file.read()
    cfg.read_string(txt)
    
    previous = cfg['General configuration']['language']

    if len(sys.argv) >= 3 and sys.argv[1] == '-set':

        assert sys.argv[2] in available_languages, 'unknown language'
        lines = txt.splitlines()
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith('language'):
                lines[i] = line.replace(previous, sys.argv[2])
                i = len(lines)
            i += 1

        with open(f'{base}\\data\\config.ini', 'w') as file:
            file.write('\n'.join(lines))
        return 'Language has been changed to "{}".'.format(available_languages[sys.argv[2]])

    elif len(sys.argv) >= 2 and (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        return 'Tap "language" to see available languages or'\
               ' "language -set <short-language-name>" to change the language.'
    txt = 'Available languages are: {}.'.format(
        ', '.join((L.replace(l, f'({l})', 1) for l, L in available_languages.items())))
    return txt + '\n"{}" is currently used.'.format(available_languages[previous])


if __name__ == "__main__":
    setup()
    print(main(base_, available_languages_))

