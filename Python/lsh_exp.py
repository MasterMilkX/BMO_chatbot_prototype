# Library imports
import numpy as np
import spacy
import math
import time
from datetime import datetime
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from nltk.corpus import stopwords
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from tabulate import tabulate
import gensim
import multiprocessing

nlp = spacy.load("en_core_web_sm")

# External file imports
from lsh import VanillaLSH


### EXPERIMENTAL VARIABLES ###

WRITE_TO_FILE = True  # write the results to a file
MULTIPROCESS = True
NUM_PROCESSES = 6  # number of processes to use for multiprocessing


k_set = [1,2,5,10,15,25]  # k values to try  (not using 100 or 250 - preliminary results on subset show that it is not worth it)
l_set = [1,5,10,25,100,250]  # l values to try
# k_set = [1]
# l_set = [1]

cur_datetime = datetime.now().strftime("%m-%d-%y %H%M")
DAT_FILE = f"../data/exp_res/LSH_EXP-[{cur_datetime}].txt"  # save the results to

prompts = [
    "a pixel skateboarding game in a cyberpunk future",                  #recs: the ramp, jet set radio, cyberpunk 2077
    "a cute, relaxing, atmospheric farming rpg with animal characters",  #recs: stardew valley, night in the woods, a short hike
    "a physics shopping simulator in a 90s mall"                   #recs: goat simulator, retrowave, donut county
] 

prompt_inc = [["THE RAMP", "JET SET RADIO", "CYBERPUNK 2077"],
                ["STARDEW VALLEY", "NIGHT IN THE WOODS", "A SHORT HIKE"],
                ["GOAT SIMULATOR", "RETROWAVE", "DONUT COUNTY"]
            ]

### SETUP AND DATA IMPORT ###

# import the dataset
def loadFeatData():
    DAT = {}
    # with open("../data/game_datfeat_FULL.txt", "r") as f:
    with open("../data/game_datfeat.txt", "r") as f:
        lines = [l.strip() for l in f.readlines()]
        CUR_GAME = ""
        for l in lines:
            # empty line (between entries)
            if l == "":
                continue
            #new entry
            else:
                if l[0] == "+":
                    CUR_GAME = l[2:]
                    DAT[CUR_GAME] = {"tags":[],"entities":[],"features":[]}
                elif l[0] == "#":
                    DAT[CUR_GAME]["tags"] = [t.lower() for t in l[2:].split(",")]
                elif l[0] == "@":
                    DAT[CUR_GAME]["entities"] = l[2:].split(",")
                elif l[0] == "-":
                    DAT[CUR_GAME]["features"].append(l[2:])
    return DAT


#get all of the tags and the entities from the game data
def getTagsEntities():
    # get all of the tags and entities
    ALL_TAGS = []
    ALL_ENTITIES = []
    for g in GAME_DATA:
        ALL_TAGS += [t.lower() for t in GAME_DATA[g]["tags"]]
        ALL_ENTITIES += [e.lower() for e in GAME_DATA[g]["entities"]]

    # remove duplicates
    ALL_TAGS = list(set(ALL_TAGS))
    ALL_ENTITIES = list(set(ALL_ENTITIES))

    return ALL_TAGS, ALL_ENTITIES


GAME_DATA = loadFeatData()
ALL_TAGS, ALL_ENTITIES = getTagsEntities()


### TOKENIZATION AND VECTORIZATION ### 

#tokenizes the text
custom_stopwords = ["game", ",", ".", "!"]
def tokenize(txt):
    raw_toks = word_tokenize(txt)
    toks = [w.lower() for w in raw_toks if w.lower() not in stopwords.words("english") and w.lower() not in custom_stopwords]
    #add the custom tag words (can be compound words)
    for t in ALL_TAGS:
        if t in txt and t not in toks:
            toks.append(t)
    return toks


### BAG OF WORDS VECTORIZATION

# create the encoding format for the bag of words
# returns array of all tokens to represent the vector
def makeBag():
    # get the set of all tags and entities
    TOKENs = []
    TOKENs += ALL_TAGS
    TOKENs += ALL_ENTITIES
    TOKENs = [t for t in list(set(TOKENs))]  #make unique
    TOKENs.sort()

    #enumerate into a set
    TOKEN_SET = {}
    for i, t in enumerate(TOKENs):
        TOKEN_SET[t] = i

    return TOKEN_SET

# return encodingq for a bag of words
# returns vectorization of the list of words given
def getBag(bag_idx, words):
    bag = [0 for _ in range(len(bag_idx))]
    for w in words:  #assume all words in bag for speed
        if w in bag_idx:
            bag[bag_idx[w]] = 1
    return bag


# encode each game as a bag of words set
# returns: {game_name: vector}
def bagGames(bag_idx):
    # encode each game as a bag of words
    BAG_GAMES = {}
    for g in tqdm(list(GAME_DATA.keys()), desc="Encoding games as bag of words"):
        game = GAME_DATA[g]
        bag = getBag(bag_idx, game["tags"]+game["entities"])
        BAG_GAMES[g] = bag

    return BAG_GAMES


### DOC2VEC VECTORIZATION ###


# simplifies the prompt by tokenizing and turn into one string
def simplify(prompt):
    #tokenize the prompt
    prompt_toks = tokenize(prompt)
    #turn into one string
    prompt_str = " ".join(prompt_toks)
    return prompt_str

# encode all of the games for doc2vec and return the model and game vectors
# returns model, {game_name: vector}
def encodeGames():
    # tokenize all of the games
    GAMES = {}
    for g in tqdm(GAME_DATA, desc="Tokenzing games"):
        tags = GAME_DATA[g]["tags"]   # get the tags
        ents = GAME_DATA[g]["entities"]  # get the entities
        
        txt = " ".join(tags + ents)   # combine the tags and entities
        txt_toks = simplify(txt)   # tokenize the text

        GAMES[g] = txt_toks
    
    #preprocess for doc2vec and return tokens for each game
    doc_games_in = {}
    with tqdm(total=len(GAMES), desc="Preprocessing games for doc2vec") as pbar2:
        for i, k in enumerate(GAMES.keys()):
            s = GAMES[k]
            tokens = gensim.utils.simple_preprocess(s)

            # For training data, add tags
            doc_games_in[k] = gensim.models.doc2vec.TaggedDocument(tokens, [i])
            pbar2.update(1)

    # train the doc2vec model
    d2vmodel = gensim.models.doc2vec.Doc2Vec(vector_size=100, min_count=2, epochs=40)
    d2vmodel.build_vocab(list(doc_games_in.values()))

    #get each game's vectors
    game_vecs = {}
    with tqdm(total=len(doc_games_in), desc="Training doc2vec model"):
        for game, tok in doc_games_in.items():
            game_vecs[game] = d2vmodel.infer_vector(tok.words)

    return d2vmodel, game_vecs

# get the doc2vec vectors for a prompt
def getDocVec(d2vmodel, prompt):
    #tokenize the prompt
    prompt_toks = tokenize(prompt)

    #infer on the model to return the vector
    return d2vmodel.infer_vector(prompt_toks)


### WORD2VEC VECTORIZATION ###

# encode the games for word2vec and average the vectors for each word to get the game vector
# returns in the form {game_name: vector} and glove data
def gameW2V():
    #retrieve the glove data
    GLOVE_DAT = {}
    with open("../data/glove.6B/glove.6B.50d.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in tqdm(lines, desc="Loading GloVe vectors"):
            line = line.split()
            GLOVE_DAT[line[0]] = np.array([float(x) for x in line[1:]])

    # create averaged vectors for each game in the set
    game_vecs = {}
    for g in tqdm(GAME_DATA.keys(), desc="Encoding games as word2vec"):
        tags = GAME_DATA[g]["tags"]
        ents = GAME_DATA[g]["entities"]
        txt = " ".join(tags + ents)
        txt_toks = tokenize(txt)

        # get the glove vectors for each word
        vecs = []
        for t in txt_toks:
            if t in GLOVE_DAT:
                vecs.append(GLOVE_DAT[t])
        
        # average the vectors
        if len(vecs) > 0:
            game_vecs[g] = np.mean(vecs, axis=0)
        
    return GLOVE_DAT, game_vecs

# gets the word2vec vector for a prompt
def getW2VVec(glove_dat, prompt):
    #tokenize the prompt
    prompt_toks = tokenize(prompt)

    # get the glove vectors for each word
    vecs = []
    for t in prompt_toks:
        if t in glove_dat:
            vecs.append(glove_dat[t])
    
    # average the vectors
    if len(vecs) > 0:
        return np.mean(vecs, axis=0)
    else:
        return None


### LSH EXPERIMENTS ###


# run the LSH experiment
def run_exp(K,L, ndim, game_vecs, prompt_vec_func):
    exp_start = time.time()
    print("Running LSH experiment with K={}, L={}".format(K,L))


    # create the LSH object
    van_lsh = VanillaLSH(K,L, 1, ndim)

    # add the games to the LSH
    hash_time = 0
    start = time.time()
    game_idx = []
    for key,v in tqdm(game_vecs.items(), desc="Hashing LSH"):
        van_lsh.hash(v)
        game_idx.append(key)
    end = time.time()
    hash_time = end-start


    # get the recommendations
    prompt_recs = {}
    for i, p in enumerate(prompts):
        prompt_vec = prompt_vec_func(p)
        rec_idx = van_lsh.query(prompt_vec)
        recs = [game_idx[i] for i in rec_idx]
        prompt_recs[i] = recs

    # format as a table for clean output
    res_tab = {}
    # headers = ["k", "l", "hastime", "# recs", "% recs / all games", "% recs inc"]
    for i, p in enumerate(prompts):
        match = 0
        for r in prompt_inc[i]:
            if r in prompt_recs[i]:
                match += 1
        res_tab[i] = [K, L, hash_time, len(prompt_recs[i]), f"{round((len(prompt_recs[i]) / len(GAME_DATA))*100)}%", f"{round((match / len(prompt_inc[i]))*100)}%"]

    exp_end = time.time()
    print(f"FINISHED (k={K},l={L})! Experiment time: {exp_end-exp_start:4f}\n")
    return res_tab

# setup vector-based parameters
class PromptQueryFun():
    def __init__(self, vec_func, opts=None):
        self.vec_func = vec_func
        self.opts = opts
    def __call__(self, x):
        return self.vec_func(self.opts, x)

# run everything altogether
def main_exp(vector_method, tofile=True):

    # make the vectors (run this once)
    stime = time.time()
    if vector_method == "doc2vec":
        D2V_MODEL, GAME_VECS = encodeGames()
    elif vector_method == "bag_of_words":
        VEC_IDX = makeBag()
        GAME_VECS = bagGames(VEC_IDX)
    elif vector_method == "word2vec":
        GLOVE_DAT, GAME_VECS = gameW2V()
    else:
        print("Invalid vector method")
        return
    etime = time.time()
    print(f"Vectorization time: {etime-stime:4f}")


    if vector_method == "doc2vec":
        pq = PromptQueryFun(getDocVec, D2V_MODEL)
        ndim = D2V_MODEL.vector_size
    elif vector_method == "bag_of_words":
        pq = PromptQueryFun(getBag, VEC_IDX)
        ndim = len(VEC_IDX)
    elif vector_method == "word2vec":
        pq = PromptQueryFun(getW2VVec, GLOVE_DAT)
        ndim = 50

    if tofile:
        with open(DAT_FILE, "a+") as f:
            f.write(f"==================         VECTOR METHOD: {vector_method} | NDIM: {ndim}       ================\n\n\n")
    
    print(f"Vector method: {vector_method}")
    print(f"Number of dimensions: {ndim}")

    # setup the results table for output to the file later
    RESULTS_TABLE = {}
    for i, p in enumerate(prompts):
        RESULTS_TABLE[i] = []

    # multi process
    if MULTIPROCESS:
        # create the pool
        pool = multiprocessing.Pool(processes=NUM_PROCESSES)

        # create the arguments
        args = []
        for ki in k_set:
            for li in l_set:
                args.append((ki, li, ndim, GAME_VECS, pq))

        # run the experiments
        for i, res in enumerate(pool.starmap(run_exp, args)):
            for k, v in res.items():
                RESULTS_TABLE[k].append(v)
            # print(f"Finished experiment {i+1} of {len(args)}")

        # close the pool
        pool.close()
        pool.join()

    # single process
    else:
        for ki in k_set:
            for li in l_set:
                # run the experiment
                res = run_exp(ki, li, ndim, GAME_VECS, pq)
                for k, v in res.items():
                    RESULTS_TABLE[k].append(v)
            

    # export results to the file
    if tofile:
        headers = ["k", "l", "hastime", "# recs", "% recs / all games", "% recs inc"]
        with open(DAT_FILE, "a+") as f:
            for i, p in enumerate(prompts):
                f.write(f"Prompt #{i+1}: {str(tokenize(p))}\n")
                f.write(tabulate(RESULTS_TABLE[i], headers, tablefmt='psql'))
                f.write("\n\n\n")
    else:
        headers = ["k", "l", "hastime", "# recs", "% recs / all games", "% recs inc"]
        for i, p in enumerate(prompts):
            print(f"Prompt #{i+1}: {str(tokenize(p))}")
            print(tabulate(RESULTS_TABLE[i], headers, tablefmt='psql'))
            print("\n\n\n")



if __name__ == "__main__":
    #show stats
    if WRITE_TO_FILE:
        with open(DAT_FILE, "w+") as f:
            stat_tab = [["# of games", len(GAME_DATA)], ["# of tags", len(ALL_TAGS)], ["# of entities", len(ALL_ENTITIES)]]
            f.write(f"{tabulate(stat_tab)}\n\n")

    for VECTOR_TYPE in ["bag_of_words", "doc2vec", "word2vec"]:
        main_exp(VECTOR_TYPE, tofile=WRITE_TO_FILE)