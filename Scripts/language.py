# -*- coding:Utf-8 -*-

import sys
import os
from configparser import ConfigParser

available_languages = {'fr': 'français', 'en': 'english'}

def main():
    cfg = ConfigParser()
    base = os.environ.get('BASE')
    with open(f'{base}\\data\\config.ini', 'r') as file:
        txt = file.read()
    cfg.read_string(txt)
    
    previous = cfg['General configuration']['language']
    
    if len(sys.argv) >= 3 and sys.argv[1] == '-set':
    
        assert sys.argv[2] in available_languages, ('unknown language')
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
        return 'Tap "language" to see available languages or "language -set <short-language-name>" to change the language.'

    txt = 'Available languages are: {}.'.format(', '.join((L.replace(l, f'({l})', 1) for l, L in available_languages.items())))
    return txt + '\n"{}" is currently used.'.format(available_languages[previous])


if __name__ == "__main__":
    print(main())

