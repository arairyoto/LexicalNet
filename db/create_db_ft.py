# coding: utf-8
import os
import sys
import logging
import codecs
import sqlite3

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)

def loadTxtModel(file_name, attr):
    f = codecs.open(file_name, 'r', 'utf-8')
    lines = f.readlines()
    res = []
    for idx, l in enumerate(lines):
        #最後の改行を除いてスペースでスプリット
        temp = l.replace("\n", "").split(" ")
        name = temp[0]
        # In the case of Synset
        if len(word.split(':'))==1:
            word = name
            lang = 'NONE'
        # In the case of Word
        elif len(word.split(':'))==2:
            word = name.split(':')[0]
            lang = name.split(':')[1]
        # In the case of Lemma
        elif len(word.split(':'))==3:
            w = name.split(':')[0]
            lang = name.split(':')[1]
            s = name.split(':')[2]
            word = s+':'+w

        embedding = temp[1:]
        embedding = ' '.join(embedding)

        if attr in ['word', 'lemma', 'synset', 'domain']:
            res.append((word, attr, lang, embedding))
        else:
            logger.warn('INVALID ATTRIBUTE: %s', attr)

    if attr in ['word', 'lemma', 'synset', 'domain']:
        sql = 'insert into '+TABLE_NAME+' (name, attr, lang, vector) values (?,?,?,?)'
        c.executemany(sql, res)
        logger.info('ATTRIBUTE:%s LANGUAGE:%s DONE', attr, lang)
    else:
        logger.warn('INVALID ATTRIBUTE: %s', attr)

if __name__ == '__main__':
    DB_NAME = 'wsl_emb.db'
    TABLE_NAME = 'emb_ft'
    FOLDER = '/Users/ryotoarai/DeskTop/ae'
    # connect to sqlite database
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # langs = ['eng', 'fra', 'jpn']
    attrs = ['word', 'synset', 'lemma']

    try:
        create_table = 'create table '+TABLE_NAME+' (name, attr, lang, vector)'
        c.execute(create_table)
    except:
        logger.warn('ALREADY CREATED TABLE')

    for attr in attrs:
        if attr in ['word', 'synset', 'lemma', 'domain']:
            loadTxtModel(FOLDER+"/"+attr+"s.txt", attr)
        else:
            logger.warn('INVALID ATTRIBUTE: %s', attr)

    conn.commit()
    # disconnect to the sqlite database
    conn.close()
