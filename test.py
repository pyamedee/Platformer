# -*- coding: utf-8 -*-

import sqlite3

data_base_connection = sqlite3.connect('data.db')
cursor = data_base_connection.cursor()

a = cursor.execute('''SELECT id, base_pos_x, base_pos_y, label
FROM LevelBaseInfo JOIN BackgroundType on BackgroundType.bg_id = LevelBaseInfo.bg_id''')

b = cursor.execute('''SELECT id, level_id, pos_x, pos_y, label
FROM LevelStructures JOIN StructureType on LevelStructures.type = StructureType.structure_id''')

print('Levels :', *a, sep='\n', end='\n\n')
print('Level\'s Structure :', *b, sep='\n')
