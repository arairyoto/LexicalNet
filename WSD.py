import os
import sys
import logging

from nltk.corpus import stopwords
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
import re
import codecs
import difflib

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)

class WSD:
    def __init__(self):
        # initialize freq_table
        self._freqs = {}
        self.stops = set(stopwords.words("english"))

    def __getitem__(self, synset):
        return self._freqs[synset]

    def lesk(self, sentence):
        res = []
        sentence = sentence.split(' ')

        for w in sentence:
            try:
                res.append(lesk(sentence, w).name())
            except:
                continue

        return res

    def lesk_process(self, sentences):
        logger.info('PROCESSING...')
        logger.info('TOTAL SENTENCES: %i', len(sentences))
        for idx, sentence in enumerate(sentences):
            if idx%1000==0:
                logger.info('PROGRESS: %i SENTENCES DONE', idx)
            sentence = re.split(r' +', sentence)
            sentence = [w for w in sentence if not w in self.stops]
            for w in sentence:
                try:
                    synset = lesk(sentence, w).name()
                    word = wn.morphy(w)
                    if word not in wn.synset(synset).lemma_names():
                        _, word = max((difflib.SequenceMatcher(None, word, l).ratio(), l) for l in wn.synset(synset).lemma_names())

                    lemma = synset+':'+word
                    if lemma not in self._freqs.keys():
                        self._freqs[lemma] = 0
                    self._freqs[lemma] += 1
                except:
                    continue
        logger.info('DONE')

    def formatter(self, text):
        text = re.sub(r"[^A-Za-z0-9^,.\/']", " ", text)
        text = re.sub(r"what's", "what is ", text)
        text = re.sub(r"\'s", " ", text)
        text = re.sub(r"\'ve", " have ", text)
        text = re.sub(r"can't", "cannot ", text)
        text = re.sub(r"n't", " not ", text)
        text = re.sub(r"i'm", "i am ", text)
        text = re.sub(r"\'re", " are ", text)
        text = re.sub(r"\'d", " would ", text)
        text = re.sub(r"\'ll", " will ", text)
        text = re.sub(r",", " ", text)
        text = re.sub(r"\.", " ", text)
        text = re.sub(r"!", "", text)
        text = re.sub(r"\/", " ", text)
        text = re.sub(r"\^", "", text)
        text = re.sub(r"\+", "", text)
        text = re.sub(r"\-", "", text)
        text = re.sub(r"\=", "", text)
        text = re.sub(r"\:", "", text)
        text = re.sub(r"\;", "", text)
        text = re.sub(r"'", " ", text)
        text = re.sub(r"-", "", text)
        return text

    def input(self, file_name):
        logger.info('LOADING: %s', file_name)
        f = codecs.open(file_name, 'r', 'utf-8')
        sentences = f.readlines()
        sentences = [self.formatter(sentence) for sentence in sentences]
        logger.info('DONE')
        return sentences

    def output(self, file_name):
        logger.info('EXPORT: %s', file_name)
        f = codecs.open(file_name, 'w', 'utf-8')
        for l,c in self._freqs.items():
            f.write(l+' '+str(c)+'\n')
        f.close()
        logger.info('DONE')

    def main(self, input_file_name, output_file_name):
        # Loading input file
        sentences = self.input(input_file_name)
        # processing sentence
        self.lesk_process(sentences)
        # output file
        self.output(output_file_name)


if __name__=='__main__':

    input_file_name = 'wsd_input/choco_review_back.txt'
    output_file_name = 'wsd_output/freq_choco.txt'

    wsd = WSD()
    wsd.main(input_file_name, output_file_name)
