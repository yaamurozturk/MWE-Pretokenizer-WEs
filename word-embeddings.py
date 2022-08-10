import spacy, csv
nlp = spacy.load("fr_core_news_sm")
from spacy.lang.fr.stop_words import STOP_WORDS as fr_stop
import gensim
from gensim import models
from gensim.models import Word2Vec

with open('lemmas-pretokenized/test-2.csv', newline='') as f:
    reader = csv.reader(f)
    data = list(reader)

"""
 The skipgram model learns to predict a target word thanks to a nearby word. 
  On the other hand, the cbow model predicts the target word according to its
  context. 
   The context is represented as a bag of the words contained in a fixed size
   window around the target word.
    
     """
model = gensim.models.Word2Vec( 
            window = 5,
                min_count = 1,
                    workers=4
                    )

model2 = gensim.models.Word2Vec( 
            window = 5,
                min_count = 1,
                    workers=4,
                        sg = 1,
                        )


model.build_vocab(data, progress_per = 100)
model2.build_vocab(data, progress_per = 100)
model.train(data, total_examples=model.corpus_count,
             epochs=model.epochs)
model.save("we-models/word2vec_models/model_1_french_short_CBOW.model")

model2.train(data, total_examples=model.corpus_count,
             epochs=model.epochs)
model2.save("we-models/word2vec_models/model_1_french_short_SkipGram.model")

