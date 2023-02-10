import pandas as pd
from dataclasses import dataclass
from conllu_df_new import Conllu_df_parser
import conllu
import numpy as np
import gensim
import itertools
import scipy.spatial.distance import pdist
import numpy as np
import re
from typing import Union
from tqdm import tqdm, trange
import matplotlib.pyplot as plt
from scipy import interpolate as sci

"Takes a cupt file and word2vec models as inputs" 

model= gensim.models.Word2Vec.load("word2vec_models/model_1_french_short_SkipGram.model")
file = "example.cupt.file"


"This part is the same as pretokenizer script.
These lines are to remove cells that are annotated as Numerical values, proper
names or punctuations, some lemmas are annotated as underscore we remove them
as well. 20-25 are optional, can be commented out if you don't want to
preprocess." 
parser = Conllu_df_parser(file)
df = parser.get_df_no_tt() 
df = df[df['upos'] != "NUM"]
df = df[df['lemma'] != "_" ]
df = df[df['upos'] != "PROPN"]
df = df[df['upos'] != "PUNCT"]
df = df.reset_index()

df[df["parseme:mwe"].str.match(r"[1-9]") == True] 
mwe = df[df["parseme:mwe"].str.match(r"[1-9]") == True] #matches all tokens of mwes (not end and start seperately)
mwe_begin = mwe[mwe["parseme:mwe"].str.match(r"[1-9]:\w+")]
    # mwe_begin["parseme:mwe"].str.cat
mwe_rest = mwe[mwe["parseme:mwe"].str.match(r"[1-9]$")]
mwe_rest.groupby(["sentence_id", "parseme:mwe"]).head()

index_mwe = df["parseme:mwe"].str.match(r"[1-9]") == True
mwe = df[index_mwe]                                                     # Matches all tokens of mwes (not end and start seperately)
# mwe_rest = mwe[mwe["parseme:mwe"].str.match(r"[1-9]$")]                 # Match the rest of the MWEs (not the beggining)
#####
mwe_rest = mwe.copy()
mwe_rest["parseme:mwe"] = mwe_rest["parseme:mwe"].str.split(":").apply(lambda x: x[0])
#####
per_sentence = mwe_rest.groupby(["sentence_id", "parseme:mwe"])
out = per_sentence["lemma"].transform(lambda x: x.str.cat(sep = "_"))   # Group them up and concatenate them
mwe_rest["lemma"] = out                                                 # Replace them in the lemmas column of the dataframe
cpdf = df.copy()
cpdf.loc[index_mwe, "lemma"] = mwe_rest["lemma"]
out = cpdf.drop(cpdf[cpdf["parseme:mwe"].str.match(r"[1-9]$")].index)

###DISPARITY#####
    
    """
    This function samples lemmas with a certain percentage given by the fraction 
    df: MWE dataframe
    fraction: percentage of random sample of items from an axis of object
    """
def get_sample_matrix(df: pd.DataFrame, fraction):
    tmp = df.sample(frac = fraction)
    return tmp[tmp.lemma.str.match(r'(\w+_\w+)')].lemma.unique()

def disparity_matrix(mwes, model):
 """
 gets a mwe list and word embeddings model
 
  """
distances = pdist(mwes, lambda x, y: (1 -model.wv.similarity(x, y)) / 2)
sums = np.sum(distances)
n = mwes.shape[0]
               
return sums/(((n-1)*(n-2))/2)

def get_pct_disparity(df: pd.DataFrame, pct: Union[float, np.float64], model, oov):
    samples = get_sample_matrix(df, pct)
    disp = disparity(samples, model)
    return disp

def get_all_pct_disparity(df, model, rg, oov):
        d = []
        for p in rg:
            d.append(get_pct_disparity(df, p, model, oov))
        return np.array(d)


def disparity(mwes: list, model):
        """
        Given a MWE list, and a model, computes the disparity

        mwes : list
        model: a model of pretrained word embeddings
        """
        pairs = []
        distance = []

        for pair in itertools.combinations(mwes, r=2):
            pairs.append((list(pair)))

        for pair in pairs:
            word1 = pair[0]
            word2 = pair[1]
            distance.append((1 - model.wv.similarity(word1, word2)) / 2)


        sums = np.sum(distance                                           
        av = sums/len(pairs)

        return av
                        


#out of vocabulary for some reasons
oov = ["faire_le_quatre-cents_coup", "se_mettre_en_quatre", "dormir_sur_son_deux_oreille", "mettre_en_le_emporter"]
pct = np.arange(20, 120, 20)/100
#pct = np.concatenate([[.01], pct],)
n_repeats = 10  

valid_df = out[~out.lemma.isin(oov)].copy()

#Disparity matrix

disparities = np.zeros((n_repeats, len(pct)))
for _ in trange(n_repeats):
    disparities[_] = get_all_pct_disparity(valid_df, model, pct, oov)

disparities.mean(axis=1)

#disparities.tofile("disparitiesx.csv", sep= ",")                      

#box plot

n_val = 100

#disparity = np.array([disp20, disp40, disp60, disp80, disp_all])*100
pct_sample_size = np.arange(20, 120, 20)
#pct_sample_size = np.concatenate([[.01], pct_sample_size],)
plt.xticks(pct_sample_size)
bp = plt.boxplot(disparities*100, labels = pct_sample_size)  

bp = plt.xlabel("sample sizes")

bp = plt.ylabel("disparity estimations")
