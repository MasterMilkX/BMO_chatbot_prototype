# extracts features from a game description using a grammar

import numpy as np
import spacy
import re

nlp = spacy.load("en_core_web_sm")

GRAMMARS = ["(VERB)(.*?)( NOUN)","(VERB)(.*?)( CCONJ)( NOUN)","(VERB)(.*?)( ADP)( NOUN)"]
GAME_DESC_FILE = "data/game_desc.txt"
MAX_SEGMENTS = 7


# cleans up the text
def cleanTxt(txt):
    txt = txt.replace("\r","").replace("\t","").replace("\n","")
    txt = re.sub(r'[^\x00-\x7F]+',' ', txt)
    txt = re.sub(r'\s*[:;/_]\s*','', txt)
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
def getFeatures(desc,debug=False):
    #split by sentence
    sentences = [s.strip() for s in desc.split(".") if s.strip() != ""]

    #break up into text and part of speech
    texts = []
    pos = []
    for s in sentences:
        doc = nlp(s)
        texts.append([t.text for t in doc])
        pos.append([t.pos_ for t in doc])

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



if __name__ == "__main__":

    game_data = {}
    # with open(GAME_DESC_FILE,"r") as f:
    with open("../data/mini_desc.txt","r") as f:
        # read in everything
        raw_txt = f.readlines()

        # separate by game and description
        games = raw_txt[::3]
        desc = raw_txt[1::3]

        for i in range(len(games)):
            game_data[games[i].strip()] = getFeatures(desc[i])

        print(game_data)
    