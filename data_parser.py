# -*- coding:Utf-8 -*-

import os


def get_data():
    with open('data.txt', 'r') as file:
        data_dict = dict()
        for line in file:
            if len(line) > 2:
                key, data_type, value = line.split(' ')
                if value.endswith('\r\n'):
                    value = value[:-2]
                else:
                    value = value[:-1]
                if data_type == 'integer':
                    value = int(value)
                elif data_type == 'path':
                    value = os.path.realpath(value[1:-1])

                data_dict[key] = value
    return data_dict


data = get_data()
