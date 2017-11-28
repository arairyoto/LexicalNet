import os
import sys
import logging
#WordNet
import nltk
from nltk.corpus import WordNetCorpusReader
from nltk.corpus import wordnet as wn

import numpy as np
import codecs
import csv

import sqlite3

from configs import *

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)

def to_lemma(s_name, w_name):
    return s_name+':'+w_name

class LexicalNet:
    def __init__(self):
        # defined in configs.py
        self.db = DB_NAME
        self.v_table = VECTOR_TABLE_NAME
        self.f_table = FREQ_TABLE_NAME
        # connect to database
        conn = sqlite3.connect(self.db)
        self.c = conn.cursor()

    def get_freq(self, name, attr, lang, categ):
        if attr == 'lemma':
            if categ==None:
                res = self.WSLObj(name, attr, lang).to_WnObj().count()/LEMMA_COUNT
            else:
                sql = 'select freq from '+self.f_table+' where name="'+name+'" and lang="'+lang+'" and categ="'+categ+'"'
                try:
                    res =  float(self.c.execute(sql).fetchone()[0])
                except:
                    res = 0
        else:
            res = 0
        return res

    def get_vector(self, name, attr, lang, categ):
        if attr in ['synset', 'domain', 'lemma']:
            if attr in ['synset', 'domain']:
                sql = 'select vector from '+self.v_table+' where name="'+name+'" and attr="'+attr+'"'
            else:
                sql = 'select vector from '+self.v_table+' where name="'+name+'" and attr="'+attr+'" and lang="'+lang+'"'
            try:
                vector =  np.array([float(x) for x in self.c.execute(sql).fetchone()[0].split(' ')])
            except:
                vector = np.zeros(300)
        elif attr == 'word':
            print(categ)
            if categ==None:
                sql = 'select vector from '+self.v_table+' where name="'+name+'" and attr="'+attr+'" and lang="'+lang+'"'
                try:
                    vector =  np.array([float(x) for x in self.c.execute(sql).fetchone()[0].split(' ')])
                except:
                    vector = np.zeros(300)
            else:
                vector = np.zeros(300)
                for synset in wn.synsets(name):
                    lemma = synset.name()+':'+name
                    vector += self.get_freq(lemma, 'lemma', lang, categ)*self.get_vector(synset.name(), 'synset', lang, categ)
        else:
            vector = np.zeros(300)

        return vector

    def all_synsets(self):
        res = []
        sql = 'select name from '+self.v_table+' where attr="synset"'
        for s in self.c.execute(sql).fetchall():
            s_name = s[0]
            res.append(WSLObject(self, s_name, 'synset'))
        return res

    def synsets(self, word, lang='eng'):
        res = []
        for s in wn.synsets(word, lang=lang):
            res.append(WSLObject(self, s.name(), 'snyset'))
        return res

    def all_words(self, lang='eng'):
        res = []
        sql = 'select name from '+self.v_table+' where attr="word" and lang="'+lang+'"'
        for w in self.c.execute(sql).fetchall():
            w_name = w[0]
            res.append(WSLObject(self, w_name, 'word', lang=lang))
        return res

    def words(self, synset_name, lang='eng'):
        res = []
        s = wn.synset(synset_name)
        for l in s.lemmas():
            res.append(WSLObject(self, l.name(), 'word', lang=lang))
        return res

    def all_lemmas(self, lang='eng'):
        res = []
        sql = 'select name from '+self.v_table+' where attr="lemma" and lang="'+lang+'"'
        for l in self.c.execute(sql).fetchall():
            l_name = w[0]
            res.append(WSLObject(l_name, 'lemma', lang=lang))
        return res

    def WSLObj(self, name, attr, lang):
        return WSLObject(self, name, attr, lang=lang)

    def to_WSLObj(self, wn_obj):
        obj_name = wn_obj.__class__.__name__
        if obj_name == 'Synset':
            res = WSLObject(self, wn_obj.name(), 'synset')
        elif obj_name == 'Lemma':
            name = wn_obj.synset().name()+':'+wn_obj.name()
            lang = wn_obj.lang()
            res = WSLObject(self, name, 'lemma', lang=lang)
        elif obj_name == 'str':
            res = WSLObject(self, wn_obj, 'word', lang='eng')
        else:
            res = None
        return res

# Object or word ,synset, lemma
class WSLObject:
    def __init__(self, ln, name, attr, lang = 'None'):
        self.name = name
        self.attr = attr
        self.lang = lang
        self.ln = ln

    def vector(self, categ=None):
        return self.ln.get_vector(self.name, self.attr, self.lang, categ)

    def freq(self, categ=None):
        return self.ln.get_freq(self.name, self.attr, self.lang, categ)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def to_WnObj(self, lang='eng'):
        res = None
        if self.attr == 'synset':
            res = wn.synset(self.name)
        elif self.attr == 'lemma':
            synset = self.name.split(':')[0]
            word = self.name.split(':')[1]
            for l in wn.synset(synset).lemmas(lang=lang):
                if l.name() == word:
                    res = l
        elif self.attr == 'word':
            res = name
        else:
            res = None
        return res

class LexicalFeature:
    def normalized_vector(self, o, categ=None):
        if categ == None:
            vec = o.vector()
        else:
            vec = o.vector(categ=categ)
        return vec/np.sqrt(sum(vec*vec))

    def relatedness(self, o_in, o_out, categ=None):
        vec_in = self.normalized_vector(o_in, categ)
        vec_out = self.normalized_vector(o_out, categ)
        return sum(vec_in*vec_out)

    def topic_relatedness(self, tw, o, domain=False):
        if domain:
            try:
                t = WSLObject(tw.name, 'domain')
            except:
                return None
        else:
            t = WSLObject(tw.name, 'word', lang=tw.lang)

        return self.relatedness(t, o)

    def ambiguity(self, w):
        synsets = [s.name() for s in wn.synsets(w.name, lang=w.lang)]
        return len(synsets), synsets

    def _ambiguity(self, w):
        lemmas = [WSLObject(to_lemma(s.name(), w.name, lang=w.lang), 'lemma') for s in wn.synsets(w.name, lang=w.lang)]
        freqs = {}
        for l in lemmas:
            freqs[l.tWnObj().synset().name()] = l.freq()
        # normalize
        for l in freqs.keys():
            freqs[k] /= sum(freqs.values())
        # TODO
        return np.var(freqs.values()), freqs

    def commonality(self, w_in, w_out):
        S_in = set([s for s in wn.synsets(w_in.name, lang=w_in.lang)])
        S_out = set([s for s in wn.synsets(w_out.name, lang=w_out.lang)])
        S_common = S_in & S_out
        return len(S_common), list(S_common)

    def _commonality(self, w_in, w_out):
        return None

    def universality(self, w):
        return None

    def _universality(self, w):
        return None

    def shortest_path(self, w_in, w_out):
        spds = []
        for s_in in wn.synsets(w_in.name, lang=w_in.lang):
            for s_out in wn.synsets(w_out.name, lang=w_out.lang):
                spds.append(s_in.shortest_path_distance(s_out))
        return min(spds)

    def associativeness(self, w_in, w_out):
        return None

if __name__=='__main__':
    ln = LexicalNet()
    synset = wn.synset('hot.a.01')
    word = 'hot'
    lemma = 'hot.a.01:hot'
    synset = ln.to_WSLObj(synset)
    word = ln.to_WSLObj(word)
    lemma = ln.WSLObj('hot.a.02:hot', 'lemma', 'eng')
    print(word.vector(categ='chocolate'))
