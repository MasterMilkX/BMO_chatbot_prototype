## BMO CHATBOT CLASS DEFINITION
# Author: Milk + Github Copilot (WOW!)
# Last modified: 2022-10-05

from asyncio.format_helpers import extract_stack
import random

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


class BMO():
    def __init__(self,debug=False):
        #set debug mode
        self.DEBUG = debug
        if self.DEBUG:
            self.debugTxt("-- DEBUG MODE --")

        #import the saved category words
        self.saveWords = self.importCategories()  #import the saved keywords
        self.exitWords = ["bye", "goodbye", "see ya", "see you later", "cya", "later", "quit", "exit"]  #words that stops the interaction
        self.extra_stopwords = ["help","need","want"]  #words that are not relevant to the categorization

        
    

    ####   SAVED WORDS FUNCTIONS  ####
    
    # parse the categories to associate relevant words 
    def importCategories(self):
        saveWords = {}
        catTxt = open("category_words.txt", "r").readlines()
        cat = ""
        for line in catTxt:
            line = line.strip()

            #nothing or comment
            if line == "" or line[0] == "#":
                continue
            #new category
            elif line[0] == "$":
                cat = line[2:]
                if cat not in saveWords:
                    saveWords[cat] = []
            #new word
            elif line[0] == "+":
                word = line[2:]
                saveWords[cat].append(word)

        self.debugTxt(saveWords)
        return saveWords

    #export the category data back out to the file
    def exportCategories(self):
        header_comments = "# Puts relevant words into categories \
        \n# Syntax: \
        \n#   # = comment (do not read) \
        \n#   $ = topic header \
        \n#   + = word"

        with open("category_words.txt", "w+") as f:
            #add the header comment
            f.write(header_comments)

            #add the categories and words
            for cat in self.saveWords:
                f.write("\n\n$ " + cat)
                for word in self.saveWords[cat]:
                    f.write("\n+ " + word)
            
    # save a new word to the keywords dictionary
    def addNewWord(self, word, category):
        self.saveWords[category].append(word)

    #add a new category to the keywords dictionary
    def addNewCategory(self, category):
        self.saveWords[category] = []

    # figure out what the user specifically wants
    # possible options: [debug, make sprites, new game features, exit]
    def matchCategory(self, resp):
        return self.rawClosestMatch(resp, self.saveWords)

    #adds more words to a particular category to associate later
    def associateWords(self, words, category):
        #add locally
        for word in words:
            self.addNewWord(word, category)

        #export to file
        self.exportCategories()

        

    ####   CONVERSATION FUNCTIONS  ####

    # show the BMO message in a format that shows BMO as the speaker
    def formBMO(self,msg):
        print("BMO: " + msg)

    # show the user message in a format that shows the user as the speaker
    def formUser(self):
        print("> ", end="")
        msg = input()
        return msg

    def debugTxt(self,txt):
        if self.DEBUG:
            print(f"% {txt} %")

    # continuously have a conversation with the user until they say goodbye (in some form or another)
    def talk(self):
        #intro
        self.formBMO("Hi there! I'm BMO, the game dev chatbot!")
        self.formBMO("What do you need? I'll do my best to help you out!")
        user_resp = self.formUser()

        #keep talking until exit
        while user_resp.lower() not in self.exitWords:
            #determine what the user wants
            user_req, words = self.matchCategory(user_resp)
            self.debugTxt(words)
            self.debugTxt(f"GUESS => {user_req}")

            #unknown request - maybe add the words to the category
            if user_req == "?":
                #figure out where the words associated fit in
                self.formBMO("I'm sorry, I don't understand...")
                self.formBMO("Is this related to code debugging, making sprites, or new game features?")

                #get the user's response for a new category
                user_cat_resp = self.formUser()

                #made by copilot (thanks!)
                cat_keywords = {
                    "code debug": ["debug", "debugging", "bug", "bugs", "error", "errors", "fix", "fixing", "code", "programming"],
                    "sprite generation": ["sprite", "sprites", "art", "graphics", "graphic", "image", "images", "picture", "pictures"],
                    "game feature idea": ["feature", "features", "game", "games", "new"]
                }
                best_cat, _ = self.rawClosestMatch(user_cat_resp, cat_keywords)

                #skip if the user doesn't want to add a new category, or can't be understood
                if best_cat == "?":
                    self.formBMO("Ok!")
                #add request words to the category
                else:
                    self.formBMO(f"Ok, I'll remember that for next time!")
                    self.associateWords(words, best_cat)


            #perform action based on user request
            elif user_req == "code debug":
                self.formBMO("I can help you debug your code!")
                print("*** [ DEBUG CODE HERE ] ***")
            elif user_req == "sprite generation":
                self.formBMO("I can help you make sprites!")
                print("*** [ GENERATE NEW SPRITES HERE ] ***")
            elif user_req == "game feature idea":
                self.formBMO("I can help you come up with new game feature ideas!")
                print("*** [ MAKE NEW GAME FEATURES HERE ] ***")

            #get the next user input
            user_resp = self.formUser()

        self.formBMO("See ya later!")

    
        
        

    #associate a raw user response to the closest matching group
    def rawClosestMatch(self,resp,wgroups):
        #tokenize the response for analysis
        raw_toks = word_tokenize(resp)
        toks = [w.lower() for w in raw_toks if w.lower() not in stopwords.words("english") and w.isalpha() and w not in self.extra_stopwords]

        #make word counts for each category
        group_ct = {}
        for k in wgroups:
            group_ct[k] = 0
        group_ct["?"] = 0

        #count the words in each category
        n = list(wgroups.keys())
        g = list(wgroups.values())
        for t in toks:
            wi = self.wordGroupIndex(t,g)
            if len(wi) > 0:
                for i in wi:
                    group_ct[n[i]] += 1
            else:
                group_ct["?"] += 1

        self.debugTxt(group_ct)

        #get the majority category
        return max(group_ct, key=group_ct.get), toks

    #find all matching indices of a word in a list of list of words
    def wordGroupIndex(self, w, gset):
        return [i for i,group in enumerate(gset) if w in group]

        


    ####   EXTRA FUNCTIONS  ####

    # show the face of BMO as ascii art
    def showFace(self):
        bmo_ascii = open("bmo_ascii.txt", "r").readlines()
        for line in bmo_ascii:
            print(line, end="")
        print("")

    ## below was written by Github Copilot -- holy fucking shit.... ##
    def copilot_intro_test(self):
        print("Hello World!")
        print("I am a chatbot prototype.")
        print("I am not very smart yet.")
        print("I can only say hello and goodbye.")
        print("What is your name?")
        name = input()
        print("Hello " + name + "!")
        print("Goodbye " + name + "!")
        print("I hope you enjoyed your time with me.")
        print("Goodbye World!")
