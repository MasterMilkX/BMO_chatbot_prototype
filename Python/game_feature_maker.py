# extracts features from a game description using a grammar

import numpy as np
import spacy
import re
from tqdm import tqdm
import json
import pandas as pd

nlp = spacy.load("en_core_web_sm")

# GRAMMAR EXTRACTION VARIABLES
GRAMMARS = ["(VERB)(.*?)( NOUN)","(VERB)(.*?)( CCONJ)( NOUN)","(VERB)(.*?)( ADP)( NOUN)"]
MAX_SEGMENTS = 7

# FILE I/O
GAME_DESC_FILE = "data/game_desc.txt"
GAME_TAG_FILE = "data/tag_games.txt"
GAME_FEAT_OUT_FILE = "data/game_datfeat.txt"

# MAIN FUNCTION VARIABLES
MODE = "features"
MY_GAMES = ["Among Us","Baba is You","Batman: Arkham City","BattleBlock Theater®","The Binding of Isaac","Castle Crashers","Caveblazers","Chroma Squad","Cuphead","Cyberpunk 2077","Downwell","Donut County","The Elder Scrolls V: Skyrim","ELDEN RING","Emily is Away Too","Escape Simulator","FEZ","Goat Simulator","Grand Theft Auto V","Hades","Hammerwatch","Hyper Light Drifter","Jet Set Radio","Kindergarten","Kingsway","Last Call BBS","Mini Ninjas","Mirror's Edge","Monster Prom","Nidhogg","Night in the Woods","OMORI","Outer Wilds","Overcooked! 2","Portal","Quadrilateral Cowboy","The Ramp","Retrowave","Scribblenauts Unlimited","A Short Hike","Spelunky","Stardew Valley","Streets of Rogue","Super Fancy Pants Adventure","Super Meat Boy","Thief","Trombone Champ","Ultrakill","Undertale","Vampire Survivors"] #use a temp set of games for testing (some faves from my steam game library)


# cleans up the text
def cleanTxt(txt):
    txt = txt.replace("\r","").replace("\t","").replace("\n","")
    txt = re.sub(r'[^\x00-\x7F]+',' ', txt)
    txt = re.sub(r'\s*[;/_]\s*','', txt)
    txt = re.sub(r'\s([\,\.])','\\1', txt)
    return txt


# merges overlapping intervals in a list
# from https://www.geeksforgeeks.org/merging-intervals/ because i failed comp. theory twice lol
def mergeIntervals(arr):
    arr.sort(key = lambda x: x[0])
    m = []
    s = -10000
    maxInt = -100000
    for i in range(len(arr)):
        a = arr[i]
        if a[0] > maxInt:
            if i != 0:
                m.append((s,maxInt))
            maxInt = a[1]
            s = a[0]
        else:
            if a[1] >= maxInt:
                maxInt = a[1]
    if maxInt != -100000 and (s, maxInt) not in m:
        m.append((s, maxInt))
    return m


# grab the features from a game description
def getFeatures(desc):
    #split by sentence
    sentences = [s.strip() for s in desc.split(".") if s.strip() != ""]

    #break up into text and part of speech
    texts = []
    pos = []
    pos_super = []
    for s in sentences:
        doc = nlp(s)
        texts.append([t.text for t in doc])
        pos.append([t.pos_ for t in doc])
        pos_super.append([t.tag_ for t in doc])

    # print(sentences)

    #find the features using REGEX
    features = []
    pos_ind_set = []
       
    for i in range(len(texts)):    
        pos_ind = []
        for cur_gram in GRAMMARS:
            
            full_pos = " ".join(pos[i])

            # get the matches using regex
            # print(full_pos)
            matches = re.finditer(cur_gram,full_pos)
                
            # convert matches back to text
            for m in matches:

                # get positions
                si = m.start(0)
                ei = m.end(0)

                # get number of spaces
                space_start = full_pos[:si].count(" ")
                space_end = full_pos[:ei].count(" ")

                # check if too many segments
                if space_end-space_start > MAX_SEGMENTS:
                    continue

                #check if the correct grammar type (for verb usage)
                if "(VERB)" in cur_gram:
                    # check if the verb is in the base tense
                    if pos_super[i][space_start] != "VB":
                        continue

                pi = (space_start,space_end)
                if pi not in pos_ind:
                    pos_ind.append(pi)

                #get the text from the number of spaces (1 pos : 1 text token)
                # features.append(" ".join(texts[i][space_start:space_end+1]))

            # print(f"{cur_gram}: {pos_ind}")

        pos_ind_set.append(pos_ind)

    # merge overlapping position intervals together
    all_pos_ind_set = [mergeIntervals(p) for p in pos_ind_set]
    # print(pos_ind_set)

    # get the blurbs from the overlaps
    for i in range(len(all_pos_ind_set)):
        for p in all_pos_ind_set[i]:
            s = p[0]
            e = p[1]

            #get the text from the number of spaces (1 pos : 1 text token)
            full_txt = " ".join(texts[i][s:e+1])
            features.append(full_txt)

    #clean up feature syntax
    features = [cleanTxt(f) for f in features if f != ""]
    return features


# show the parts of speech specifically for verbs
# def showpart(txt):
#     doc = nlp(txt)
#     text = [t.text for t in doc]
#     pos = [t.pos_ for t in doc]
#     tag = [t.tag_ for t in doc]

#     print(text)
#     print(pos)
#     print(tag)
#     print("")

# showpart("jump on powerlines")    #VB
# showpart("picks up in the titular metropolis")   #VBZ
# showpart("bending trials")        #VBG




# get the noun entities from the game description (for semantic reasoning later)
def getEntities(desc):
    doc = nlp(desc)
    #get all nouns and proper nouns
    valid_set = ["NOUN"]
    nouns = [t.text.lower() for t in doc if t.pos_ in valid_set]
    return np.unique(nouns)


###############       MAIN      ####################


# get the features from a file and sort them by tag
if __name__ == "__main__":

    FULL_GAME_TAGS = []
    GAME_DATA = {}

    #get the game names and tags
    with open(GAME_TAG_FILE,"r") as f:
        tag_txt = f.readlines()
        # genres = tag_txt[::2]
        # all_games = tag_txt[1::2]

        #kinda inconsistent with grabbing genres to games
        genres = []
        all_games = []
        i = 0
        while(i < len(tag_txt)):
            if tag_txt[i].strip() == "":
                i += 1
                continue
            else:
                genres.append(tag_txt[i].strip())
                all_games.append(tag_txt[i+1].strip())
                i += 2
        # print(f"Found {len(genres)} genres and {len(all_games)} games")
        FULL_GAME_TAGS = [g.strip() for g in genres]

        #break up the game names
        with tqdm(total=len(all_games)) as pbar:
            for i in range(len(all_games)):
                game_list = all_games[i].split("|")
                game_list = [cleanTxt(g).strip().upper() for g in game_list]
                for g in game_list:
                    if g not in GAME_DATA:
                        GAME_DATA[g] = {"tags":[],"features":[],"entities":[]}
                    GAME_DATA[g]["tags"].append(genres[i].strip())
                pbar.update(1)

    # print(game_data['Terraria'])
    print("# Games: ",len(GAME_DATA))
    print("# Tags: ",len(FULL_GAME_TAGS))






    #make the co-occurence matrix between tags
    if MODE == "matrix":
        #alphabetize the tags
        FULL_GAME_TAGS = sorted(FULL_GAME_TAGS)

        #make the matrix
        CO_TAG_MATRIX = np.zeros((len(FULL_GAME_TAGS),len(FULL_GAME_TAGS)))
        tags = [sorted(gd["tags"]) for gd in GAME_DATA.values()]
        with tqdm(total=len(tags)) as pbar:
            for gt in tags:
                for i in range(len(gt)):
                    for j in range(len(gt)):
                        if i == j:
                            continue
                        else:
                            CO_TAG_MATRIX[FULL_GAME_TAGS.index(gt[i]),FULL_GAME_TAGS.index(gt[j])] += 1
                pbar.update(1)

        #export the matrix
        comatrix = pd.DataFrame(CO_TAG_MATRIX,index=FULL_GAME_TAGS,columns=FULL_GAME_TAGS)
        comatrix.astype(int).to_csv("data/tag_matrix.csv")


    #extract features from the games and save them to the full dataset
    elif MODE == "features":

        # print([k for k in GAME_DATA.keys() if "LIFE IS STRANGE" in k])
        # exit()

        #read in the game data with descriptions
        skipped = []
        num_features = 0
        with open(GAME_DESC_FILE,"r") as f:
            # read in everything
            raw_txt = f.readlines()

            # separate by game and description
            games = [cleanTxt(g).strip().upper() for g in raw_txt[::3]]
            desc = raw_txt[1::3]
            GDESC = dict(zip(games,desc))

            #for each game, extract the features
            # with tqdm(total=len(games)) as pbar:
            #     for game in games:
            with tqdm(total=len(MY_GAMES)) as pbar:
                MY_GAMES = [cleanTxt(g).strip().upper() for g in MY_GAMES]
                for game in MY_GAMES:
                    pbar.set_description(game)

                    if not (game in GAME_DATA and game in GDESC):  
                        # print(f"{game} not found in GAME_DATA or GDESC")
                        skipped.append(game)
                        continue

                    #grab the features
                    features = getFeatures(GDESC[game])
                    num_features += len(features)
                    GAME_DATA[game]["features"] = features

                    #grab the entities
                    entities = getEntities(GDESC[game]).tolist()
                    entities += getEntities(game.lower()).tolist()
                    GAME_DATA[game]["entities"] = np.unique(entities)

                    pbar.update(1)
                    
        print(f"Extracted [ {num_features} ] features")
        print(f"Skipped [ {len(skipped)} ] games")

        #export the data to a txt file (each game has + in front, tag list has a #, entity list has a @, everything else is a feature on a new line)
        with open(GAME_FEAT_OUT_FILE,"w+") as f:
            # for k,v in GAME_DATA.items():
            for k in MY_GAMES:
                v = GAME_DATA[k]
                f.write(f"+ {k}\n")
                f.write(f"# {','.join(v['tags'])}\n")
                f.write(f"@ {','.join(v['entities'])}\n")
                for feat in v["features"]:
                    f.write(f"{feat}\n")
                f.write("\n") 
            

    