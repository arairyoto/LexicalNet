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
from LexicalNet import *

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)

ln = LexicalNet()
lf = LexicalFeature()

class Evaluation:
    def ambiguity_test(self, contexts, words):
        f = open('evaluation/amb.txt', 'w')
        f_ = open('evaluation/amb_.txt', 'w')
        # HEADER
        for c in contexts:
            f.write(','+c)
            f_.write(','+c)
        f.write('\n')
        f_.write('\n')

        for w in words:
            f.write(w)
            for c in contexts:
                w_in_c = ln.to_WSLObj(w, categ=c)
                amb, _ = lf.ambiguity(w_in_c)
                amb_, __ = lf._ambiguity(w_in_c)
                f.write(','+str(amb))
                f_.write(','+str(amb_))
            f.write('\n')
            f_.write('\n')
        f.close()
        f_.close()

    def topic_relatedness_test(self, contexts, words):
        f = open('evaluation/tr.txt', 'w')
        # HEADER
        for c in contexts:
            f.write(','+c)
        f.write('\n')

        for w in words:
            f.write(w)
            for c in contexts:
                ctxt = ln.to_WSLObj('CATEG:'+c)
                w_in_c = ln.to_WSLObj(w, categ=c)
                rel = lf.relatedness(w_in_c, ctxt)
                f.write(','+str(rel))
            f.write('\n')
        f.close()

    def associative_test(self, c, w):
        f = open('evaluation/ass_'+w+'_'+c+',txt', 'w')
        w_in_c = ln.to_WSLObj(w, categ=c)
        for w in ln.all_words(categ=c):
            _, rel, sp = lf.associativeness(w_in_c, w)
            f.write(w.name+','+str(rel)+','+str(sp)+'\n')
        f.close()

    def space_test(self, contexts, words):
        f = open('evaluation/space.txt', 'w')
        for c in contexts:
            for w in words:
                name = w+':'+c
                w_in_c = ln.to_WSLObj(w, categ=c)
                vec = ' '.join([str(e) for e in w_in_c.vector()])
                f.write(name+' '+vec+'\n')
        f.close()

if __name__=='__main__':
    ev = Evaluation()
    contexts = ['automotive', 'music', 'clothing']
    words = ['cold', 'warm', 'bright', 'dark', 'soft', 'hard', 'dynamic', 'static']
    # space validation
    ev.space_test(contexts, words)
    #ambiguity
    ev.ambiguity_test(contexts, words)
    #topic relatedness
    ev.topic_relatedness_test(contexts, words)

    for c in contexts:
        for w in words:
            ev.associative_test(c,w)
