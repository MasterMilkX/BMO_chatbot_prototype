## GENERAL UTILITY FUNCTION FOR THE BMO PROJECT
# for use in notebooks or other code

import spacy
import math
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords



#########     GLOBAL VARIABLES     #########

CUSTOM_STOPWORDS = ["game", ",", ".", "!"]

nlp = spacy.load("en_core_web_sm")



##########     TFIDF FUNCTIONS     ##########

# used in the context where docs = games and their descriptional entities

#term frequency - how often a term appears in a document / total number of terms in the document
def tf(doc):  # assume doc is a list of words already tokenized
    tf_dict = {}
    for word in doc:
        if word not in tf_dict:
            tf_dict[word] = 1
        tf_dict[word] += 1
    for word in tf_dict:
        tf_dict[word] = tf_dict[word] / len(doc)
    return tf_dict

#inverse document frequency - log(total number of documents / number of documents with term t in it)
def idf(documents):  # assume documents is a list of lists of words already tokenized
    df = {}
    for doc in documents:  
        for word in doc:
            if word not in df:
                df[word] = 0
            df[word] += 1
    idf_dict = {}
    for word in df:
        idf_dict[word] = math.log(len(documents) / df[word])
    return idf_dict
    
# get the full tfidf score for each word in each game's dataset
def tfidf(doc_set):  # assume doc_set is a dictionary of games with word lists already tokenized
    tfidf_dict = {}
    corpuses = [d for d in doc_set.values()]
    idf_dat = idf(corpuses)
    for game, doc in doc_set.items():
        tf_dat = tf(doc)
        tfidf_dict[game] = {}
        for word in doc:
            tfidf_dict[game][word] = tf_dat[word] * idf_dat[word]  
    return tfidf_dict

# same as above, but only uses the idf data from the given doc_set
def idf_docs(doc_set):
    idf_dict = {}
    corpuses = [d for d in doc_set.values()]
    idf_dat = idf(corpuses)
    for game, doc in doc_set.items():
        idf_dict[game] = {}
        for word in doc:
            idf_dict[game][word] = idf_dat[word]  
    return idf_dict



######    IMPORT THE SCRAPED GAME DATA    ######

#import the game data from the game_datfeat.txt file
def importGameData(self,full=True):
    #select which file to import
    if full:
        print("Importing full game data...")
        game_import_file = "../data/game_datfeat_FULL.txt"
    else:
        print("Importing subset of game data...")
        game_import_file = "../data/game_datfeat.txt"

    #import the data
    DAT = {}
    with open(game_import_file, "r") as f:
        lines = [l.strip() for l in f.readlines()]
        CUR_GAME = ""
        for l in lines:
            # empty line (between entries)
            if l == "":
                continue
            #new entry
            else:
                if l[0] == "+":
                    CUR_GAME = l[2:].upper()
                    DAT[CUR_GAME] = {"tags":[],"entities":[],"features":[]}
                elif l[0] == "#":
                    DAT[CUR_GAME]["tags"] = [t.lower() for t in l[2:].split(",")]
                elif l[0] == "@":
                    DAT[CUR_GAME]["entities"] = [e.lower() for e in l[2:].split(",")]
                elif l[0] == "-":
                    DAT[CUR_GAME]["features"].append(l[2:])

    return DAT

#get all of the tags and the entities from the game data
# returns a tuple of (tags, entities)
def getTagsEntities(self,game_data):
    # get all of the tags and entities
    ALL_TAGS = []
    ALL_ENTITIES = []
    for g in game_data:
        ALL_TAGS += [t.lower() for t in game_data[g]["tags"]]
        ALL_ENTITIES += [e.lower() for e in game_data[g]["entities"]]

    # remove duplicates and set the value
    return list(set(ALL_TAGS)), list(set(ALL_ENTITIES))

# tokenize a prompt from the list of tags
def tokenize(txt):
    raw_toks = word_tokenize(txt)
    toks = [w.lower() for w in raw_toks if w.lower() not in stopwords.words("english") and w.lower() not in CUSTOM_STOPWORDS]
    return toks

# extract and singularize the nouns from a prompt
def single_noun(txt):
    doc = nlp(txt)
    toks = [t.lemma_ for t in doc if t.pos_ == "NOUN"]
    return toks