import pandas as pd
from conllu_df_new import Conllu_df_parser
import conllu


file = "../MTLB-STRUCT/code/saved/predictions/0-50-16.cupt"
parser = Conllu_df_parser(file)
df = parser.get_df_no_tt() 

df = df.reset_index()
df = df[df['upos'] != "NUM"]
df = df[df['lemma'] != "_" ]
df = df[df['upos'] != "PROPN"]
df = df[df['upos'] != "PUNCT"]

print(df.head())

# df[df["parseme:mwe"].str.match(r"[1-9]") == True] 
mwe = df[df["parseme:mwe"].str.match(r"[1-9]") == True] #matches all tokens of mwes (not end and start seperately)
mwe_begin = mwe[mwe["parseme:mwe"].str.match(r"[1-9]:\w+")]
# mwe_begin["parseme:mwe"].str.cat
mwe_rest = mwe[mwe["parseme:mwe"].str.match(r"[1-9]$")]
mwe_rest.groupby(["sentence_id", "parseme:mwe"]).head()


index_mwe = df["parseme:mwe"].str.match(r"[1-9]") == True
mwe = df[index_mwe]                                                     # Matches all tokens of mwes (not end and start seperately)
#mwe_rest = mwe[mwe["parseme:mwe"].str.match(r"[1-9]$")]                 # Match the rest of the MWEs (not the beggining)
#####
mwe_rest = mwe.copy()
mwe_rest["parseme:mwe"] = mwe_rest["parseme:mwe"].str.split(":").apply(lambda x: x[0])
#####
per_sentence = mwe_rest.groupby(["sentence_id", "parseme:mwe"])
out = per_sentence["lemma"].transform(lambda x: x.str.cat(sep = "_"))   # Group them up and concatenate them
mwe_rest["lemma"] = out                                                 # Replace them in the lemmas column of the dataframe
#cpdf = df.copy()
df.loc[index_mwe, "lemma"] = mwe_rest["lemma"]
out = df.drop(df[df["parseme:mwe"].str.match(r"[1-9]$")].index)

print(out[out["sentence_id"] == 999][1:-1])



pd.options.display.max_colwidth = 1009

out_lemmas = out[['sentence_id', 'lemma']]
out_sentences = out_lemmas.groupby('sentence_id').agg(lambda x: x.tolist())
print(out_sentences[2643:])

lemmas_list = out_sentences["lemma"].tolist()

import csv

with open("data/lemmas-pretokenized/0-50-16.cupt", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(lemmas_list)

print("pretokenized and listed in csv")








