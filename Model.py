# -*- coding:Utf-8 -*-

import sqlite3
from logger import logger


class Model:

    def __init__(self):
        logger.debug('initialize Model')
        self.database_connection = sqlite3.connect('data.db')
        self.cursor = self.database_connection.cursor()

    def get_text(self, languages, text_id=-1):

        code = '''SELECT id, ''' + ', '.join(languages) + ''' FROM Text'''
        if text_id != -1:
            code += ' WHERE id = {}'.format(text_id)

        return self.cursor.execute(code)

    def get_level(self, level_id=-1):

        code = '''SELECT id, base_pos_x, base_pos_y, label
        FROM LevelBaseInfo JOIN BackgroundType on LevelBaseInfo.bg_id = BackgroundType.bg_id'''
        args = []

        if level_id != -1:
            code += ' WHERE id = ?'
            args.append(level_id)

        return self.cursor.execute(code, args)

    def get_structures(self, level_id=-1, structure_id=-1):

        code = '''SELECT id, level_id, pos_x, pos_y, label
        FROM LevelStructures JOIN StructureType on LevelStructures.type = StructureType.structure_id'''

        args = []

        if structure_id != -1:
            code += ' WHERE id = ?'
            args.append(structure_id)

        elif level_id != -1:
            code += ' WHERE level_id = ?'
            args.append(level_id)

        return self.cursor.execute(code, args)

    def structure_getter(self, level_id=-1):
        return self._StructureGetter(self.get_structures(level_id))

    class _StructureGetter:
        def __init__(self, structures):
            self._structures = tuple(structures)
            self._dif = self._structures[0][0]

        def __getitem__(self, index):
            return self.get(index)

        def get(self, index, default=None):
            try:
                if index < 1:
                    raise IndexError
                value = self._structures[index - self._dif]
            except IndexError:
                if default is not None:
                    return default
                raise IndexError('id "{}" does not exist or is out of range'.format(index))
            return value

        def __repr__(self):
            tab = tuple(repr(a) for a in self._structures)
            return 'struct([' + (',\n' + ' ' * 8).join(tab) + '])'

        def __str__(self):
            return repr(self._structures)

        def __iter__(self):
            return iter(self._structures)


if __name__ == '__main__':
    model = Model()
    text = model.get_text(('en',), 1)
    print(list(text))

