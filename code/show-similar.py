import gensim
from gensim import models
from gensim.models import Word2Vec
import pandas as pd 
import numpy as np

#pd.options.display.max_colwidth = 1000
model= gensim.models.Word2Vec.load("word2vec_models/model_1_french_short_SkipGram.model")
model2= gensim.models.Word2Vec.load("word2vec_models/model_1_french_short_CBOW.model")


pairs = [["tenir_conférence", "tomber_amoureux"], ["chien", "mettre"],['voler',
'donner'],["remettre_le_main_à_le_pâte", "chien"],
["remettre_le_main_à_le_pâte", "aider"], ["avoir_raison", "se_tromper"],
["perdre","gagner"],["mettre_fin", "finir"] , ["mettre_fin", "commencer"], ["perdre", "retenir_attention"], ["exprimer", "se_traduire"]]

opposites = []
for pair in pairs:
    word1 = pair[0]
    word2 = pair[1]
    opposites.append(model.wv.similarity(word1, word2))
list_opposites = list(zip(pairs, opposites))
print(list_opposites)
    


#assert  count_pandas == nocc, "Number of occurences wasn't the same "

file = "../lemmas-pretokenized/test-2.csv"
with open(file, "r") as f:
    s = f.read()

list_of_mwes = ["grand", "se_adresser", "se_avérer", "se_appuyer", "soutenir",
                "attirer_attention", "mettre_fin", 
                "faire_progrès", "faire_partie", "se_diriger",
                "tenir_compte", "prendre_en_compte", "se_lever",
                "accomplir_tâche", "voler_à_secours",
                "remettre_le_main_à_le_pâte", "mettre_fin"]

frequent_in_train = ["avoir_lieu",
        "se_trouver", 
        "faire_partie",  
        "se_rendre",
        "se_situer",
        "avoir_droit",
        "jouer_rôle",
        "se_produire",
        "avoir_besoin",
        "tenir_compte",
        "se_engager",
        "faire_appel"]


s = s.replace("\n", ",").split(",")
df = pd.value_counts(np.array(s))

count_pandas = []
count_in_train = []
similars = []
similarsCbow = []
similars_train = []

for word in list_of_mwes:
    count_pandas.append(df[df.index == word][0])
    similars.append(model.wv.most_similar(word, topn=5))
    similarsCbow.append(model2.wv.most_similar(word, topn=5))
    #print(f"Number of occurences of {word}: {count_pandas} ")
    #print(similars)

for word in frequent_in_train:
    count_in_train.append(df[df.index == word][0])
    similars_train.append(model.wv.most_similar(word, topn=5))


df_mwes_count = pd.DataFrame(list(zip(list_of_mwes, count_pandas, 
    [item[0][0] for item in similars],
    [item[1][0] for item in similars],
    [item[2][0] for item in similars],
    [item[3][0] for item in similars],
    [item[4][0] for item in similars])),
        columns=['mwes',"counts", "close1", "close2", "close3", "close4", "close5"])

df_mwes_count_cbow = pd.DataFrame(list(zip(list_of_mwes, count_pandas,
        [item[0][0] for item in similarsCbow],
            [item[1][0] for item in similarsCbow],
                [item[2][0] for item in similarsCbow],
                    [item[3][0] for item in similarsCbow],
                        [item[4][0] for item in similarsCbow])),
                                columns=['mwes',"counts", "close1", "close2",
                                    "close3", "close4", "close5"])




df_mwes_train = pd.DataFrame(list(zip(frequent_in_train, count_in_train,
        [item[0][0] for item in similars_train],
            [item[1][0] for item in similars_train],
                [item[2][0] for item in similars_train],
                    [item[3][0] for item in similars_train],
                        [item[4][0] for item in similars_train])),
                                columns=['mwes',"counts", "close1", "close2",
                                    "close3", "close4", "close5"])
#print(df_mwes_count)

df_mwes_count.to_csv('similarities.csv', mode="w", sep=' ', index=False)
df_mwes_count_cbow.to_csv('similarities-cbow.csv', mode="w", sep=' ', index=False)
df_mwes_train.to_csv("similarities-freq-train.csv", mode = "w", sep = " ",
        index = False)
#print(df_mwes_count.to_string())









#print("MODEL SKIPGRAM RESULTS" + "\n" )
#print("\n"+ "grand" + "\n")
#print(model.wv.most_similar("grand"))
#print("\n"+ "se adresser" + "\n")
#print(model.wv.most_similar("se_adresser"))
#print("\n"+ "se avérer" + "\n")
#print(model.wv.most_similar("se_avérer"))
#print("\n"+ "se appuyer" + "\n")
#print(model.wv.most_similar("se_appuyer"))
#print("\n"+ "soutenir" + "\n")
#print(model.wv.most_similar("soutenir"))
#print("\n"+ "attirer attention" + "\n")
#print(model.wv.most_similar("attirer_attention"))
#print("\n"+ "mettre fin" + "\n")
#print(model.wv.most_similar("mettre_fin"))
#print("\n"+ "faire progres" + "\n")
#print(model.wv.most_similar("faire_progrès"))
#print("\n"+ "faire partie" + "\n")
#print(model.wv.most_similar("faire_partie"))
#print("\n"+ "se diriger" + "\n")
#print(model.wv.most_similar("se_diriger"))
#print("\n"+ "tenir compte" + "\n")
#print(model.wv.most_similar("tenir_compte"))
#print("\n"+ "prendre en compte" + "\n")
#print(model.wv.most_similar("prendre_en_compte"))
#print("\n" + "se lever" + "\n")
#print(model.wv.most_similar("se_lever"))
#print("\n"+ "accomplir tâche" + "\n")
#print(model.wv.most_similar("accomplir_tâche"))
##print(model2.wv.most_similar("accomplir_tâche"))
