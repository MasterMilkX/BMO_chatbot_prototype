# The game feature recommendation module for the BMO assistant game design chatbot
# Based on Experiment #7 from 'game_feature_gen_exp.ipynb'
# Written by Milk
 

# IMPORTS and SETUP
import numpy as np
import spacy
import math
import re
import random
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json
from nltk.corpus import wordnet as wn
# from nltk.stem.wordnet import WordNetLemmatizer as wnl


# other files
import sys
sys.path.append('../')
import Python.utils as utils

# setup
nlp = spacy.load("en_core_web_sm")


# GAME REC MOD CLASS (make game similarity recommendations)

class GameRecMod():
    """
    Used to select features from games that have similar themes to a prompt

    Usage:
    ------
    GameRec = GameRecModel()
    GameRec.setup()     #default uses the full dataset with a GLoVe model size of 50
     
    Attributes:
    -----------
    - self.GAME_DATA : { str : { 'tags' : list(str), 'entities' : list(str), 'features' : list(str) } }
        a set of the imported game data with the name of the game as the key and a dictionary of the game's tags, entities, and features as the value
    - self.ALL_TAGS : list(str)
        a list of tags from all the games
    - self.ALL_ENTITIES : list(str)
        a list of entities from all the games
    - self.GAME_DAT_TFIDF : { str : { str : float } }
        a dictionary of the tfidf scores for each word in each game's dataset with the game as the key and a dictionary of the words and their tfidf score as the value
    - self.GLOVE_DAT : { str : np.array(float) }
        a dictionary of the GloVe vectors for each word in the dataset with the word as the key and a numpy array of the vector as the value

    Best Methods:
    -------------
    tokenize(text) : list(str)
        tokenizes a string of text into a list of words (tokens) while removing stopwords and punctuation
    toDataStr(text) : str
        breaks a prompt text down to the tags and entities in the dataset and rewrites it as a dataset item string
    
    getGameFeats(game) : list(str)
        returns the features of a game
    getGameTags(game) : list(str)
        returns the tags of a game
    getGameEntities(game) : list(str)
        returns the entities of a game

    getClosestGames(text, num=5) : list(str), list(float)
        returns the names of the games that are most similar to the prompt text and their similarity scores
    getTopGameFeats(prompt_txt,num_games) : list(str)
        returns the features of the closest games to the prompt text; returns the features from the top num_games games
    getNumGameFeats(prompt_txt,num_feats) : list(str)
        returns the features of the closest games to the prompt text; returns the exact number of features requested
    getTopGameEntities(prompt_txt,num_entities) : list(str)
        returns the entities of the closest games to the prompt text; returns the exact number of entities requested
    
    """

    # init function
    def __init__(self):
        # big variables
        self.GAME_DATA = {}
        self.ALL_TAGS = []
        self.ALL_ENTITIES = []
        self.GAME_DAT_TFIDF = {}
        self.GLOVE_DAT = {}

        #helper variables
        self.custom_stopwords = ["game", ",", ".", "!"]

    # creates everything needed for the game recommender
    def setup(self, full=True, glove_size=50):
        self.importGameData(full=full)
        self.getTagsEntities()
        self.importGlove(size=glove_size)
        self.importGameDatTfidf()


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
        self.GAME_DATA = {}
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
                        self.GAME_DATA[CUR_GAME] = {"tags":[],"entities":[],"features":[]}
                    elif l[0] == "#":
                        self.GAME_DATA[CUR_GAME]["tags"] = [t.lower() for t in l[2:].split(",")]
                    elif l[0] == "@":
                        self.GAME_DATA[CUR_GAME]["entities"] = [e.lower() for e in l[2:].split(",")]
                    elif l[0] == "-":
                        self.GAME_DATA[CUR_GAME]["features"].append(l[2:])


    #get all of the tags and the entities from the game data
    def getTagsEntities(self):
        # get all of the tags and entities
        ALL_TAGS = []
        ALL_ENTITIES = []
        for g in self.GAME_DATA:
            ALL_TAGS += [t.lower() for t in self.GAME_DATA[g]["tags"]]
            ALL_ENTITIES += [e.lower() for e in self.GAME_DATA[g]["entities"]]

        # remove duplicates and set the value
        self.ALL_TAGS = list(set(ALL_TAGS))
        self.ALL_ENTITIES = list(set(ALL_ENTITIES))


    #import the word embedding data from the GloVe dataset
    def importGlove(self,size=50):
        GLOVE_DAT = {}
        with open(f"../data/glove.6B/glove.6B.{size}d.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in tqdm(lines,desc='Importing GloVe'):
                line = line.split()
                self.GLOVE_DAT[line[0]] = np.array([float(x) for x in line[1:]])

    
    # get the tfidf scores for each game
    def importGameDatTfidf(self):
        GAME_DOCS = {}
        for g in self.GAME_DATA:
            GAME_DOCS[g] = list(set(self.GAME_DATA[g]["tags"]+self.GAME_DATA[g]["entities"]))
        self.GAME_DAT_TFIDF = utils.idf_docs(GAME_DOCS)



    # return the similarity score between 2 game theme word sets
    # takes as input 2 lists of tokens from each game
    def gameSim(self,prompt_game,comp_game): 
        # Get the cosine similarity between each word in g1 and g2 to make a matrix
        d = cosine_similarity([self.GLOVE_DAT[w] for w in prompt_game if w in self.GLOVE_DAT],[self.GLOVE_DAT[w] for w in comp_game if w in self.GLOVE_DAT if w in self.GLOVE_DAT])

        #return the average of the max similarity score for each word in the prompt game
        return sum([max(x) for x in d])


    #tokenizes the text
    def tokenize(self, txt):
        raw_toks = word_tokenize(txt)
        toks = [w.lower() for w in raw_toks if w.lower() not in stopwords.words("english") and w.lower() not in self.custom_stopwords]
        #add the custom tag words (can be compound words)
        for t in self.ALL_TAGS:
            if t in txt and t not in toks:
                toks.append(t)
        return toks


    ### MAIN FUNCTIONS ###

    # turns the prompt into a dataset item [tags, entities]
    def toDataStr(self, txt):
        prompt_toks = self.tokenize(txt)
        tags = [t for t in prompt_toks if t in self.ALL_TAGS]
        entities = [e for e in prompt_toks if e in self.ALL_ENTITIES]
        return f"{','.join(tags)}\n{','.join(entities)}"

    # get the closest games to the prompt game
    def getClosestGames(self, prompt_txt, num_games=3):
        # get the prompt game tokens
        prompt_toks = self.tokenize(prompt_txt)

        # get the similarity scores for each game
        sim_scores = {}
        for g in self.GAME_DATA.keys():
            other_toks = self.GAME_DATA[g]['tags'] + self.GAME_DATA[g]['entities']
            sim_scores[g] = self.gameSim(prompt_toks,other_toks)

        #add tf-idf scores where found
        tot_scores = {}
        for g in sim_scores:
            for t in prompt_toks:
                if t in self.GAME_DAT_TFIDF[g]:
                    tot_scores[g] = sim_scores[g]+self.GAME_DAT_TFIDF[g][t]

        # sort the games by similarity score
        sorted_games = sorted(tot_scores.items(), key=lambda x: x[1], reverse=True)

        # return the top num_games and their distances (for debugging)
        best = sorted_games[:num_games]
        return [b[0] for b in best], [b[1] for b in best]

    # returns the list of features for a game
    def getGameFeats(self,game):
        return self.GAME_DATA[game]["features"]

    # returns the list of tags for a game
    def getGameTags(self,game):
        return self.GAME_DATA[game]["tags"]

    # returns the list of entities for a game
    def getGameEntities(self,game):
        return self.GAME_DATA[game]["entities"]

    # returns some features from the top games recommended
    def getTopGameFeats(self, prompt_txt, num_games=3):
        top_games, _ = self.getClosestGames(prompt_txt,num_games=num_games)
        feats = []
        for g in top_games:
            feats += self.getGameFeats(g)
        return feats

    # returns the first n game features from the top selected games
    def getNumGameFeats(self, prompt_txt, num_feats=30):
        top_games, _ = self.getClosestGames(prompt_txt,num_games=num_feats)  #assume each game has at least 1 feature
        feats = []
        for g in top_games:
            feats += self.getGameFeats(g)
            if len(feats) >= num_feats:
                break
        return feats[:num_feats]

    # returns some entities from the top games recommended
    def getTopGameEntities(self, prompt_txt, num_games=3):
        top_games, _ = self.getClosestGames(prompt_txt,num_games=num_games)
        ents = []
        for g in top_games:
            ents += self.getGameEntities(g)
        return list(set(ents))








# FEATURE MOD CLASS (make features)


class FeatureMod():
    """
        Uses ConceptNet to get relational entity phrases (copied from ExtConceptNetFeatGamifier) and then uses those to generate features.
    
        Parameters:
        -----------
        train_entity_set : list(str)
            list of nouns to get related entities for
        steps : int
            how many layers of related entities to get
        debug : bool
            print debug statements
        
        Attributes:
        -----------
        self.full_entity_set : list(str)
            list of all nouns in the entity set (includes input entities and entities found in ConceptNet)
        self.cnet_feats : list(str)
            list of all features found in ConceptNet using the entity set

        Methods:
        --------
        - self.generate(int): randomly choose a subset of the features to return
    """
    def __init__(self, train_entity_set,get_related=True,steps=2,debug=False):
        self.noun_rel = ['RelatedTo','PartOf','IsA','HasA','MadeOf','Synonym']
        self.verb_rel = ['CapableOf','UsedFor']
        
        # get more entities that are related to the entity set
        if get_related:
            if debug:
                print(f"> Extracting related entities from ConceptNet...")

            # increase the depth of search for related entities
            all_nouns = train_entity_set
            more_nouns = train_entity_set
            for i in range(steps):
                more_nouns = self.getThemeNouns(more_nouns,f" [{i+1}/{steps}]")
                all_nouns = list(set(all_nouns + more_nouns))
            self.full_entity_set = all_nouns
            if debug:
                print(f"> Extracted [ {len(all_nouns) - len(train_entity_set)} ] entities from ConceptNet!")
        else:
            self.full_entity_set = train_entity_set

        if debug:
            print(f"> Total [ {len(self.full_entity_set)} ] entities in the entity set!")

        # get the features based on the entity sets
        cnet_feats, dfts = self.getThemeFeats(self.full_entity_set)
        self.det_cnet_feats = dfts

        #process features (turn into base verbs)
        if debug:
            print(f"> Processing [ {len(cnet_feats)} ] features...")

        self.cnet_feats = []
        for f in cnet_feats:
            doc = nlp(f)    
            has_verb = False
            nf = []
            for t in doc:
                if t.pos_ == "VERB":
                    has_verb = True
                    nf.append(t.lemma_)
                else:
                    nf.append(t.text)
            nnf = ""
            if has_verb and len(nf) > 1:    
                nnf = " ".join(nf)
            if nnf != "":
                if nnf != "" and "be" in nf and not "be a" in nf:
                    self.cnet_feats.append(nnf.replace("be ",""))
                else:
                    self.cnet_feats.append(nnf)

        if debug:
            print(f"> FINISHED!")


    
    #use concept net to get the new entities related to it
    def getThemeNouns(self, word_set,txt=""):
        noun_set = []

        # go through each word's connections
        for word in tqdm(word_set, desc=f"Getting related nouns{txt}"):
            # get the related thematic words for a word (use same POS)
            obj = requests.get(f'http://api.conceptnet.io/c/en/{word}').json()
            for e in obj['edges']:

                #skip non-english words
                if 'language' in e['end'] and e['end']['language'] != 'en':
                    continue

                if e['rel']['label'] in self.noun_rel:
                    noun_set.append(e['end']['label'])
        
        #clean up
        return list(set(noun_set))

    #get more features from the entity set using the relational set (capableof, usedfor)
    def getThemeFeats(self, word_set):
        feat_set = []
        det_feat_set = {}

        # go through each word's connections
        for word in tqdm(word_set, desc="Getting related features"):
            det_feat_set[word] = []
            for rel in self.verb_rel:
                # get the related thematic words for a word (use same POS)
                obj = requests.get(f'https://api.conceptnet.io/query?node=/c/en/{word}&rel=/r/{rel}&offset=0&limit=30').json()
                for e in obj['edges']:

                    #skip non-english words
                    if ('language' in e['end'] and e['end']['language'] != 'en') or (e['end']['label'] in det_feat_set[word]):
                        continue

                    det_feat_set[word].append(e['end']['label'])
                    feat_set.append(e['end']['label'])
        
        #clean up
        return list(set(feat_set)), det_feat_set


    # generates a feature set from a grammar setup
    def generate(self,n=10):
        return random.sample(self.cnet_feats,n)

