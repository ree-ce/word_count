import datetime
import importlib
import os
from db_control import DbControl

def create_read_me():
    db_control = DbControl()
    db_control.open_database('words.db')
    top_words=db_control.get_top_words(100)
    db_control.close_database()

    str_md = 'word|count\n---|---\n'
    for item in top_words:
        str_md += item[0]+'|'+str(item[1])+'\n'

    with open('README.md', 'w') as f:
        f.write('# WORD COUNT\r\n')
        f.write('This repository grab words from news websites. The included urls can be checked from the word.db.\r\n')
        f.write('However, now only CNN is supported\r\n')
        f.write('Last update: '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+'\r\n')
        f.write(str_md)


def run():
    create_read_me()
    # importlib.import_module('cnn_input')


if __name__ == '__main__':
    run()
