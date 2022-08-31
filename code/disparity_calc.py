import pandas as pd
from dataclasses import dataclass
from conllu_df_new import Conllu_df_parser
import conllu
import numpy as np
import gensim
import itertools

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


def get_sample(df: str, fraction):
    #tmp = df.sample(frac = fraction, replace=True, random_state=4)
    tmp = df.sample(frac= fraction)
    lemmas = tmp[tmp.lemma.str.match(r'(\w+_\w+)')].lemma.unique()
    lemmas = lemmas.tolist()
    return lemmas



def disparity(mwes: list, model):
    pairs = []
    distance = []
    
    for pair in itertools.combinations(mwes, r=2):
        pairs.append((list(pair)))
        
    for pair in pairs:
        word1 = pair[0]
        word2 = pair[1]
        distance.append(model.wv.similarity(word1, word2))
    
    sums= np.sum(distance)
    av = sums/len(pairs)
    
    return av 


  
frac20 = get_sample(out, .20)
frac40 = get_sample(out, .40)
frac60 = get_sample(out, .60)
frac80 = get_sample(out, .80)
all_mwes = out[out.lemma.str.match(r'(\w+_\w+)')].lemma.unique().tolist()


out_of_vocab = ["faire_le_quatre-cents_coup", "se_mettre_en_quatre", "dormir_sur_son_deux_oreille"]

def out_of_v(list, words): 
    for el in out_of_vocab:
        if el in list: list.remove(el)
        return list
    
disp80 = disparity(frac80, model)
disp60 = disparity(frac60, model)
disp40 = disparity(frac40, model)
disp20 = disparity(frac20, model)
disp_all = disparity(all_mwes, model)

import matplotlib.pyplot as plt
from scipy import interpolate as sci

x = np.array([disp20, disp40, disp60, disp80, disp_all])
xx = np.linspace(x.min(), x.max(), 100)
# corresponding y axis values
y = [20, 40, 60, 80, 100]
#spline = make_interp_spline(x, y)
cb = sci.CubicSpline(x, y)
yy = cb(xx)
plt.yticks(y)
# plotting the points 
plt.plot(xx, yy)
plt.xlabel("disparity")
plt.ylabel("corpus sample size")
print(plt.grid())  
