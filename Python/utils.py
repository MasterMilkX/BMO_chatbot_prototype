## GENERAL UTILITY FUNCTION FOR THE BMO PROJECT
# for use in notebooks or other code

import spacy
import math
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import colorsys
from PIL import Image



################################                        GLOBAL VARIABLES                     ################################

CUSTOM_STOPWORDS = ["game", ",", ".", "!"]
nlp = spacy.load("en_core_web_sm")

# COLOR FUNCTIONS
PICO_PALETTE = ['#000000','#1D2B53','#7E2553','#008751','#AB5236','#5F574F','#C2C3C7','#FFF1E8','#FF004D','#FFA300','#FFEC27','#00E436','#29ADFF','#83769C','#FF77A8','#FFCCAA']



################################                        TF-IDF FUNCTIONS                      ################################

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



################################               IMPORT THE SCRAPED GAME DATA             ################################

#import the game data from the game_datfeat.txt file
def importGameData(full=True):
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
def getTagsEntities(game_data):
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




################################                           SPRITE EXTRACTION                        ################################

# convert 3 rgb values (0-255) to a hex string
def rgb2hex(r,g,b):
    return f"#{r:02x}{g:02x}{b:02x}".upper()

# convert a hex string to an rgb tuple
def hex2rgb(hex):
    h2 = hex.lstrip('#')
    return tuple(int(h2[i:i+2], 16) for i in (0, 2, 4))


# gets the closest color based on euclidean distance in RGB space
def closestColor(hex,palette=PICO_PALETTE):
    r,g,b = hex2rgb(hex)
    d = [np.linalg.norm(np.array([r,g,b]) - np.array(hex2rgb(p))) for p in palette]
    return d.index(min(d))


# return index of palette color closest to input color
# ideal weights: [1,0.25,0.5]
def closestColorHSV(c,palette=PICO_PALETTE,weight=[1,0.25,0.5]):
    c_hsv = colorsys.rgb_to_hsv(c[0]/255,c[1]/255,c[2]/255)
    p_rgb = np.array([hex2rgb(p) for p in palette])
    p_hsv = np.array([colorsys.rgb_to_hsv(p[0]/255,p[1]/255,p[2]/255) for p in p_rgb])

    #get euclidean distance in HSV space
    p_d = np.linalg.norm(np.multiply(p_hsv,weight) - np.multiply(c_hsv,weight),axis=1)
    # p_d = np.linalg.norm(p_hsv - c_hsv,axis=1)

    return int(np.argmin(p_d))

# breaks up the sprite sheet into 8x8 sprites
def getSprites(sheet,size=8,pad=2):
    sprites = []
    sheet_n = np.array(sheet)
    si = size+pad*2
    sx = len(sheet)//si
    sy = len(sheet[0])//si
    for x in range(sx): 
        for y in range(sy):
            offx = x*si+pad
            offy = y*si+pad
            sprite = sheet_n[offx:offx+size,offy:offy+size]
            # print(sprite.shape)
            sprites.append(sprite)
    return sprites

# reads in a sprite sheet and converts to an integer format based on the palette
def readSpriteSheet(filename,palette=PICO_PALETTE):
    img = Image.open(filename)
    pixels = img.load() 
    width, height = img.size

    int_img = []
    for y in range(height):
        row = []
        for x in range(width):
            if len(pixels[x,y]) == 3:
                r, g, b = pixels[x,y]
                a = 255
            else:
                r, g, b, a = pixels[x,y]
            hex = rgb2hex(r,g,b)
            if palette and hex in palette:
                val = palette.index(hex)
            else:  # if not in palette, find the closest match in the palette based on euclidean distance
                val = closestColor(hex,palette)
            row.append(val)
        int_img.append(row)
    
    return int_img

# splits pcio-9 spritesheet into individual sprites and saves them to a np array
def picoSS2np(ss_file, palette=PICO_PALETTE):
    pico_sheet = readSpriteSheet(ss_file,palette)
    pico_sprites = getSprites(pico_sheet,8,0)
    return np.array(pico_sprites)