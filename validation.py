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

class Validation:
    def __init__(self, test_file, lang):
        self.lang = lang

    def load_test_file(self):

    def test(self, w1, w2):
        word1 = LexicalNet.WSLObj(w1, 'word', self.lang)
        word2 = LexicalNet.WSLObj(w2, 'word', self.lang)

        synset1 = [LexicalNet.to_WSLObj(synset) for synset in wn.synsets(w1, lang=self.lang)]
        synset2 = [LexicalNet.to_WSLObj(synset) for synset in wn.synsets(w2, lang=self.lang)]

        lemma1 = [LexicalNet.WSLObj(synset.name()+':'+w1, 'lemma', self.lang) for synset in wn.synsets(w1, lang=self.lang)]
        lemma2 = [LexicalNet.WSLObj(synset.name()+':'+w2, 'lemma', self.lang) for synset in wn.synsets(w2, lang=self.lang)]

        return LexicalFeature.relatedness(word1, word2), self.simMax(synset1,synset2), self.simAve(synset1,synset2), self.simMax(lemma1,lemma2), self.simAve(lemma1,lemma2)

    def simMax(self, O1s, O2s):
        result = []
        for o1 in O1s:
            for o2 in O2s:
                result.append(LexicalFeature.relatedness(o1, o2))
        return max(result)

    def simAve(self, O1s, O2s):
        result = []
        for o1 in O1s:
            for o2 in O2s:
                result.append(LexicalFeature.relatedness(o1, o2))
        return sum(result)/len(result)

    def main(self):
        for i in range(N):
            w1 =
            w2 =
            w, smS, saS, smL, saL = self.test(w1, w2)
