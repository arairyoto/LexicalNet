# coding: utf-8
import os
import sys
import logging
import codecs
import sqlite3

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)

def loadTxtModel(file_name):
    f = codecs.open(file_name, 'r', 'utf-8')
    lines = f.readlines()
    res = []
    freq_total = 0
    for idx, l in enumerate(lines):
        #最後の改行を除いてスペースでスプリット
        temp = l.replace("\n", "").split(" ")
        lemma = temp[0]
        freq = int(temp[1])
        freq_total += freq
        res.append([CATEGORY, lemma, LANG, freq])

    for r in res:
        # normalize frequency
        r[3] /= freq_total
        r = tuple(r)
        print(r)

    sql = 'insert into '+TABLE_NAME+' (categ, name, lang, freq) values (?,?,?,?)'
    c.executemany(sql, res)

if __name__ == '__main__':
    DB_NAME = 'wsl_emb.db'
    TABLE_NAME = 'freq'
    CATEGORY = 'chocolate'
    LANG = 'eng'
    FILE = '../wsd_output/freq_choco.txt'
    # connect to sqlite database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # c.execute('drop table freq')

    try:
        create_table = 'create table '+TABLE_NAME+' (categ, name, lang, freq float)'
        c.execute(create_table)
    except:
        logger.warn('ALREADY CREATED TABLE')

    loadTxtModel(FILE)

    conn.commit()
    # disconnect to the sqlite database
    conn.close()
