# LexicalNet
## Description
## Setup
First, please Download WordEmbedding Database from https://www.dropbox.com/sh/s28mhihpg3g4c5b/AAATcqjYnFH-T4DbtXoR7ozKa?dl=0 and place it in 'db' folder.
## Dependencies
## Installation
## Usage

### Define LexicalNet
```
from LexicalNet import *
ln = LexicalNet()
```
### WSLObject
WSLObject is the object which is created for combining Synset and Lemma and Word Object.

You can define any of three objects mentioned above like this:
```
word = ln.WSLObj([word_name], 'word', [lang])
synset = ln.WSLObj([synset_name], 'synset')
lemma = ln.WSLObj([lemma_name], 'lemma', [lang])
```
* lemma_name is defined as '[synset_name]:[word_name]' in this system.

And also you can define WSLObject from WordNetObject like this:
```
synset = ln.to_WSLObj([SynsetObject])
lemma = ln.to_WSLObj([LemmaObject])
```

### Vector and frequency
Once you get the WSLObject you can get vector and frequency of the object like this:
```
wsl_obj = ln.WSLObj([as you like])
vector = wsl_obj.vector()
freq = wsl_obj.freq()
```
* For now, the frequency information is assigned only to lemma object.
* Frequency information is normalized so that the sum of every frequency is equal to 1.

And also you can get vector and frequency in a certain category (context) like this:
```
wsl_obj = ln.WSLObj([as you like])
vector = wsl_obj.vector(categ=[category])
freq = wsl_obj.freq(categ=[category])
```

### Lexical Feature Calculation
You can calculate following lexical features in this system.

- relatedness
- topic_relatedness
- ambiguity
- commonality
- universality
- associativeness

Each of them can be calculated like this:
```
wsl_obj1 = ln.WSLObj([as you like])
wsl_obj2 = ln.WSLObj([as you like])
topic = ln.WSLObj([topic_word] , 'word', [lang])

lf = LexicalFeature()

lf.relatedness(wsl_obj1, wsl_obj2, categ)
lf.topic_relatedness(topic, wsl_obj)
lf.ambiguity(wsl_obj)
lf.commonality(wsl_obj1, wsl_obj2)
lf.universality(wsl_obj)
lf.associativeness(wsl_obj1, wsl_obj2, categ)
```

### Categories
The categories we can use are now limited. Here are the available categories. They will be updated in the future.

- chocolate
