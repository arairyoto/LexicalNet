# coding: utf-8
import os
import sys
import logging
import codecs
import sqlite3

import numpy as np

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)


def get_vector(name):
    sql = 'select vector from '+TABLE_NAME_EMB+' where name="'+name+'" and attr="lemma" and lang="'+LANG+'"'
    try:
        vector =  np.array([float(x) for x in self.c.execute(sql).fetchone()[0].split(' ')])
    except:
        vector = np.zeros(300)
    return vector

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
        CONTEXT_VECTOR += freq*get_vector(lemma)
        res.append([CATEGORY, lemma, LANG, freq])

    for r in res:
        # normalize frequency
        r[3] /= freq_total
        r = tuple(r)
        print(r)

    sql = 'insert into '+TABLE_NAME+' (categ, name, lang, freq) values (?,?,?,?)'
    c.executemany(sql, res)

if __name__ == '__main__':
    CONTEXT_VECTOR = np.zeros(300)
    DB_NAME = 'wsl_emb.db'
    TABLE_NAME = 'freq'
    TABLE_NAME_EMB = 'emb'
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

    # insert Context Vector
    vec = ' '.join([str(e) for e in CONTEXT_VECTOR])
    d = ('CATEG:'+CATEGORY, 'word', LANG, vec)
    res = [d]
    sql = 'insert into '+TABLE_NAME_EMB+' (name, attr, lang, vector) values (?,?,?,?)'
    c.executemany(sql, res)

    conn.commit()
    # disconnect to the sqlite database
    conn.close()
