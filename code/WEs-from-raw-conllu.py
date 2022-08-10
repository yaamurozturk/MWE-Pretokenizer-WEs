from concurrent.futures import ThreadPoolExecutor
from typing import Tuple
import pyconll
import sys, os
from tqdm import tqdm
import csv
from pathlib import Path
from typing import Tuple
import time
import gensim
import spacy
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop



def parse_lemmas(conll_words_file):
    """
    Parse the lemmas in a specific file
    """
    lemmas = []
    for sentence in tqdm(conll_words_file):
        sentence_list = []
        for token in sentence:
            if not token.upos == 'PUNCT'and not token.upos == None and not token.upos == 'X' and not token.upos == 'NUM' and not token.upos == "PROPN" and token.lemma not in fr_stop: #remove some POS
                sentence_list.append(token.lemma.lower())
        lemmas.append(sentence_list)
        lemmas = [x for x in lemmas if len(x)>=10] #remove sentences that have less than 10 lemmas 
        sentences_lemmas = [' '.join(snt) for snt in lemmas]
    return sentences_lemmas



def load_file(path):
    """
    Load a specific file 
    """

    conll_words_file = pyconll.load_from_file(path)
    print('____________sentence processing ____________')
    sentences_lemmas = parse_lemmas(conll_words_file)
    return sentences_lemmas


def load_folder(name: Tuple) -> str:
    """
    Loads the whole folder
    """
    inDir, files = name
    for file in files:
        sentences_lemmas = load_file(inDir, file)
    return sentences_lemmas

def write_file(num, sentences_lemmas) -> list:
    file = f"raw{num}"
    print('______________writing to file {}____________'.format(file))
    with open("{}/{}.csv".format(inDir, file), 'w', encoding="utf-8", newline='') as g:
        writer = csv.writer(g, delimiter=',')
        for item in sentences_lemmas:
            writer.writerow([item])  

          
inDir = "24"
files = os.listdir(inDir)
abspath = [os.path.join(os.getcwd(), inDir, i) for i in files] # use os.walkdir because generators are faster
print(abspath)

''' 
t = time.time()
sen = []
for file in abspath:
    sen.append(load_file(file))
t = time.time() - t 
'''

t2 = time.time()
with ThreadPoolExecutor(3) as ex:
    for num, res in enumerate(ex.map(load_file, abspath)):
        write_file(num, res)

t2 =  time.time() - t2

print(f"Parallel time: {t2}")
