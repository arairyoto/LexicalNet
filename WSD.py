import os
import sys
import logging

import nltk
from nltk.corpus import stopwords
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
from nltk.corpus import semcor
import re
import codecs
import difflib

import inspect
import json
import pickle

# for BabelNet and Bebelfy
import urllib
import json
import gzip

from io import BytesIO

from LexicalNet import LexicalNet, LexicalFeature
from configs import *

# ログ
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)-7s %(message)s')
logger = logging.getLogger(__name__)

class WSD:
    def __init__(self):
        # initialize freq_table
        self._freqs = {}
        with open('signatures.pickle', 'rb') as f:
            self.signatures = pickle.load(f)

        self.stops = set(stopwords.words("english"))

        self.word_counter = {}

    def __getitem__(self, synset):
        return self._freqs[synset]

    def to_wordnet_pos(self, _pos):
        if _pos.startswith('NN'):
            pos = 'n'
        elif _pos.startswith('VB'):
            pos = 'v'
        elif _pos.startswith('JJ'):
            pos = 'a'
        elif _pos.startswith('RB'):
            pos = 'r'
        else:
            pos = None

        return pos

    def establich_signature(self):
        signatures = {}
        for s in semcor.tagged_sents(tag='both'):
            words = []
            for tree in s:
                if tree.label().__class__.__name__=='Lemma':
                    words.append(tree.label().name())
            words = set(words)
            print(words)
            for tree in s:
                if tree.label().__class__.__name__=='Lemma':
                    if tree.label().synset().name() not in signatures.keys():
                        signatures[tree.label().synset().name()] = set()
                    signatures[tree.label().synset().name()] |= words

        with open('signatures.pickle', 'wb') as f:
            pickle.dump(signatures, f)

    def signature(self, ss):
        if ss.name() not in self.signatures.keys():
            signature = list(ss.definition().split())
        else:
            signature = list(ss.definition().split())+list(self.signatures[ss.name()])
        return set(signature)

    def lesk(self, sentence, w):
        return lesk(sentence, w)

    def _lesk(self, context_sentence, ambiguous_word, pos=None, synsets=None):
        context = set(context_sentence)
        if synsets is None:
            synsets = wn.synsets(ambiguous_word)

        if pos:
            synsets = [ss for ss in synsets if str(ss.pos()) == pos]

        if not synsets:
            return None

        _, sense = max((len(context.intersection(self.signature(ss))), ss) for ss in synsets)

        return sense

    def count_words(self, sentences):
        logger.info('COUNTING...')
        logger.info('TOTAL SENTENCES: %i', len(sentences))
        self.total_count = 0
        for idx, sentence in enumerate(sentences):
            if idx%1000==0:
                logger.info('PROGRESS: %i SENTENCES DONE', idx)
            sentence = re.split(r' +', sentence.strip())
            sentence = [w for w in sentence if not w in self.stops]
            for w in sentence:
                word = wn.morphy(w)
                if word not in self.word_counter.keys():
                    self.word_counter[word] = 0
                self.word_counter[word] += 1
                self.total_count += 1
        logger.info('DONE')

    def calc(self, context, signature, ln, lf):
        res = 0
        k = 100 # constant

        for c in context:
            c_o = ln.to_WSLObj(c)
            for s in signature:
                s_o = ln.to_WSLObj(s)
                try:
                    res += np.log(1+self.word_conter[c]*k/self.total_count)*np.log(1+self.word_conter[s]*k/self.total_count)*lf.relatedness(c_o, s_o)
                except:
                    continue

        return res/(len(context)*len(signature))


    def prototype(self, context_sentence, ambiguous_word, ln, lf, pos=None, synsets=None):
        context = set(context_sentence)
        if synsets is None:
            synsets = wn.synsets(ambiguous_word)

        if pos:
            synsets = [ss for ss in synsets if str(ss.pos()) == pos]

        if not synsets:
            return None

        _, sense = max(((self.calc(context, set(self.signature(ss)), ln, lf)), ss) for ss in synsets)

        return sense

    def prototype_process(self, sentences, update=True):
        # Count words
        self.count_words(sentences)

        ln = LexicalNet()
        lf = LexicalFeature()

        logger.info('PROCESSING...')
        logger.info('TOTAL SENTENCES: %i', len(sentences))

        for idx, sentence in enumerate(sentences):
            if idx%1==0:
                logger.info('PROGRESS: %i SENTENCES DONE', idx)
            sentence = re.split(r' +', sentence.strip())
            sentence = [w for w in sentence if not w in self.stops]
            tagged_sentence = nltk.pos_tag(sentence)

            for wp in tagged_sentence:
                try:
                    w = wp[0] # word
                    p = self.to_wordnet_pos(wp[1]) # pos
                    if update:
                        synset = self.prototype(sentence, w, ln, lf, pos=p).name()
                    else:
                        synset = self.prototype(sentence, w, ln, lf, pos=p).name()
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

    def register(self, synset, w):
        word = wn.morphy(w)
        if word not in wn.synset(synset).lemma_names():
            _, word = max((difflib.SequenceMatcher(None, word, l).ratio(), l) for l in wn.synset(synset).lemma_names())

        lemma = synset+':'+word
        if lemma not in self._freqs.keys():
            self._freqs[lemma] = 0
        self._freqs[lemma] += 1

    def lesk_process(self, sentences, update=False):
        logger.info('PROCESSING...')
        logger.info('TOTAL SENTENCES: %i', len(sentences))
        for idx, sentence in enumerate(sentences):
            if idx%1000==0:
                logger.info('PROGRESS: %i SENTENCES DONE', idx)
            sentence = re.split(r' +', sentence.strip())
            sentence = [w for w in sentence if not w in self.stops]
            tagged_sentence = nltk.pos_tag(sentence)

            for wp in tagged_sentence:
                try:
                    w = wp[0] # word
                    p = self.to_wordnet_pos(wp[1]) # pos
                    if update:
                        synset = self._lesk(sentence, w, pos=p).name()
                        self.register(synset, w)
                    else:
                        self.babelfy(sentence)
                except:
                    continue
        logger.info('DONE')

    # http://babelfy.org/javadoc/it/uniroma1/lcl/jlt/util/Language.html
    def babelfy(self, text, lang='EN'):
        service_url = 'https://babelfy.io/v1/disambiguate'
        params = {
        	'text' : text,
        	'lang' : lang,
        	'key'  : BABEL_KEY
        }

        data = self.get(service_url, params)

        # retrieving data
        for result in data:
            # retrieving char fragment
            charFragment = result.get('charFragment')
            cfStart = charFragment.get('start')
            cfEnd = charFragment.get('end')
            w = text[cfStart:(cfEnd+1)]

            # retrieving BabelSynset ID
            synsetId = result.get('babelSynsetID')
            synset = self.bbl2wn(synsetId).name()

            self.register(synset, w)


    def bbl2wn(self, babelSynsetID):
        service_url = 'https://babelnet.io/v4/getSynset'
        params = {
        	'id' : babelSynsetID,
        	'key'  : BABEL_KEY
        }

        data = self.get(service_url, params)
        wnOffsets = data['wnOffsets']
        if len(wnOffsets)!= 0:
            wnOffsets = data['wnOffsets'][0]['mapping']['WN_30'][0]
            sense = wn.of2ss(wnOffsets)
        else:
            sense = None

        return sense

    def get(self, service_url, params):
        url = service_url + '?' + urllib.parse.urlencode(params)
        request = urllib.request.Request(url)
        request.add_header('Accept-encoding', 'gzip')
        response = urllib.request.urlopen(request)

        if response.info().get('Content-Encoding') == 'gzip':
        	buf = BytesIO(response.read())
        	f = gzip.GzipFile(fileobj=buf)
        	data = json.loads(f.read())
        else:
            data=None

        return data

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

    def _main(self, input_file_name, output_file_name):
        # Loading input file
        sentences = self.input(input_file_name)
        # processing sentence
        self.prototype_process(sentences)
        # output file
        self.output(output_file_name)


if __name__=='__main__':
    input_file_name = 'wsd_input/choco_review_back.txt'
    output_file_name = 'wsd_output/freq_choco_uprototype.txt'

    wsd = WSD()
    # wsd.establich_signature()
    wsd.main(input_file_name, output_file_name)

    # text = 'BabelNet is both a multilingual encyclopedic dictionary and a semantic network'
    # wsd.babelfy(text)
    # text = 'バベルネット は 多言語 辞書 で あり 意味 ネットワーク でも あり ます 。'
    # wsd.babelfy(text, lang='JA')
