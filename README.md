# MWE-Pretokenizer-WEs

This repository contains some of the outcome of my Master internship at LISN, Paris-Saclay University, February-August 2022.

# Context
Exploring diversity measures (including variety, balance and disparity) for the linguistic phenomenon of multiword expressions (MWEs) in French.

# Diversity
We view diversity as a measure over **items** clustered into **types**. In the context of MWEs, items are all **annotated occurrences of MWEs**, while a type is the **set of all occurrences**	 of the same MWE. Types are approximated by lemmatising lexicalized components of each MWE occurrence and considering each **multiset of lemmas** as one type. E.g. _he **paid** a **visit**_, _all the **visits** **paid** by her_ and _**paying** those **visit**_ are items of the same type {pay, visit}.

The 3 dimensions of diversity are:
- **variety** - the number of all types (occurring in an annotated corpus)
- **balance** - the evenness of the distribution of items into types
- **disparity** - the degree to which types differ from each other

This work is mostly dedicated to **disparity**.

# Objectives
- modeling disparity of MWEs in terms of static word embeddings
- assessing the feasibility of such modeling in the absence of very large manually annotated corpora
- long-distance objective: integrate diversity measures into evaluation and benchmarking of NLP tools for a variety of linguistic phenomena

# Data
- [French PARSEME corpus v 1.2](http://hdl.handle.net/11234/1-3367) annotated manually for verbal MWEs
- [French PARSEME raw corpus](https://gitlab.com/parseme/corpora/-/wikis/Raw-corpora-for-the-PARSEME-1.2-shared-task) for the PARSEME shared task 1.2 in 2020
 
# Software used
- [MTLB-STRUCT](https://github.com/shivaat/MTLB-STRUCT/) - a tool for automatic identification of verbal MWEs; scored best in the [PARSEME shared task 1.2](https://multiword.sourceforge.net/sharedtaskresults2020); the re
- []
 
# Methodology
- Automatically annotating the raw corpus for MWEs with MTLB
- Pre-processing

Re-tokenizing the raw corpus so that MWEs are merged into single tokens (including those which are discontinuous), e.g.

    _she has been **paying visits** to her friends_
    _he **paid** her a **visit**_ 
	
would be re-tokenized into 
	
    _she has been **pay_visit** to her friends_
    _he **pay_visit** her a_
	
- Training word2vec static word embeddings on the lemmas of the re-tokenized corpus
- Assessing the resulting semantic space (with exprimentally chosen MWEs)
- Calculating disparity as an average of pair-wise cosine distances between the MWE types present in the corpus

# Installation guide for re-running the whole processing chain
- Download the two PARSEME corpora and place them in a selected directory, say ``PARSEME-corpora/FR`` (for the manually annotated corpus in .cupt format), and ``PARSEME-corpora/FR-raw/raw.conllu`` (for the raw corpus in .conllu format)
- You may want to divide the raw corpus files into smaller ones, say raw-001.conllu, raw-002.conllu etc.
    ```
    $awk -v max=100000 '{print > sprintf("xx%02d", int(n/max))} /^$/ {n += 1}' raw.conllu
    ```
- Install [MTLB-STRUCT](https://github.com/shivaat/MTLB-STRUCT/), in your MTLB-STRUCT directory
- Train a French model of MTLB-STRUCT based on the French PARSEME corpus (TRAIN+DEV+TEST)
- If MTLB-STRUCT retraining is not needed, the ready-made model and config files can be found on the segur server at LISN, 
	```
	mylogin@segur:cd /vol/projcomiles/grpiles/2022-mwe-diversity-yagmur-ozturk-internship/MTLB-STRUCT/saved/FR_DEV_bert-base-multilingual-cased_multitask
	mylogin@segur:ls
	bertTaggerResults_DEV_system.cupt  config_saved.json  Idx2Tags.npy  tagger.torch
	mylogin@segur:
	```
- Prepare the PARSEME raw corpus for automatic annotation by MTLB-STRUCT
    ```
    $cd PARSEME-corpora/FR-raw
    $sed s/$/\\t_/ fr-raw.conllu > fr-raw.cupt #ADD NEW COLUMN WITH UNDERSCORE
    $vim fr-raw.cupt #REMOVE UNDERSCORES FROM EMPTY LINES: %s/^\t_$// \
                      #ADD THE FIRST LINE: global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC PARSEME:MWE
    $mv fr-raw.cupt blind.test.cupt  #RENAME THE FILE TO FOLLOW THE SHARED TASK CONVENTIONS
    $mv blind.test.cupt MTLB-STRUCT/data/1.2/FR
    ```
- Run MTLB-STRUCT with the French model to annotate the PARSEME raw corpus for MWEs
   ```
   $cd MTLB-STRUCT/code
   $python load_test.py saved/FR_DEV_bert-base-multilingual-cased_multitask
   ```
   The annotated files will be saved
	

- Download the two PARSEME corpora and place them in a selected directory

```console
cd MWE-Pretokenizer-WEs/
mkdir `
cd PARSEME-corpora
curl --remote-name-all https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3367{/README.md,/FR.tgz}
tar -xf FR.tgz

```

# History of progress

##February & March : 
-Creating bibliography about MWES:
    -> summaries for articles in "https://github.com/yaamurozturk/MultiWordExpressions_Bibliography"
    
    -> Different definitions of MWEs. 
    
    -> MWE categories in PARSEME
    
    -> Shared Tasks in PARSEME
    
    -> Specifically examining Turkish MWEs and noticing problems about lemmas. 

##April & May :
    -> Fixing the issues in the Turkish corpus of PARSEME
    
    -> Re-sampling the files in the same order of shared task.
    
    -> Readings: about Diversity measures and usage of word embeddings. 
    
    -> Article about Turkish MWEs, how lemmas can be problematic.
    
##June & July & August : 
    -> Multiword processing with word embeddings is an important subject, two possibilities : averaging the vectors of mwe tokens or pretokenizing the mwes. 
    
    -> Decision to work on disparity, implications on WEs to adapt it to linguistic phenomenon. 
    
    -> Testing word embeddings on a bigger corpus around 2M sentences from the conllu files, regardless of MWEs. (scripted)
    
    -> Turning conllu files to cupt format to make blind.test files. 
    
    -> Using the MTLB system to annotate MWEs in these raw corpora. Trained the model on PARSEME shared task. 
    
    -> Pretokenizing the MWEs in the raw corpora using the cupt parser (scripted).
    
    -> Testing the word embeddings with different sizes of data. 
    
    -> Skipgram works better than cbow according to some examples (antonyms like small-big have close vectors, not like we expected them to be represented orthogonally, but phrases that have nothing in common are further such as se retenir and arbre) 
    
    -> It is very much dependent on the number of occurrences of a phrase we have in a corpus, so good lemmatisation is indeed key to mwe processing. 
    
    
To print csv files in terminal prettier:

    -> cat xx.csv | sed 's/ / ,/g' | column -t -s, | less -S
    
- Word2vec gensim parameters: 

model = gensim.models.Word2Vec( 
    window = 5,
    min_count = 1,
    workers=4)
model2 = gensim.models.Word2Vec( 
    window = 5,
    min_count = 1,
    workers=4,
    sg = 1)

*The skipgram model learns to predict a target word thanks to a nearby word. On the other hand, the cbow model predicts the target word according to its context. 
