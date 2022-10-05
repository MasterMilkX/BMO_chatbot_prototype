## BMO CHATBOT CLASS DEFINITION
# Author: Milk + Github Copilot (WOW!)
# Last modified: 2022-10-05




# a chatbot that interfaces with code to help users debug code and create a game
from numpy import frombuffer


class BMO():
    def __init_(self):
        self.readCategories()  #import the saved keywords
        pass

    ####   CONVERSATION FUNCTIONS  ####

    # show the BMO message in a format that shows BMO as the speaker
    def formBMO(self,msg):
        print("BMO: " + msg)

    # show the user message in a format that shows the user as the speaker
    def formUser(self):
        print("> ")
        msg = input()
        return msg

    # continuously have a conversation with the user until they say goodbye (in some form or another)
    def talk(self):
        #intro
        self.formBMO("Hi there! I'm BMO, the chatbot!")
        self.formBMO("What do you need?")
        user_resp = fromUser

        #keep talking until exit
        while user_resp.lower not in ["bye", "goodbye", "see ya", "see you later", "cya", "later", "quit", "exit"]:



            user_resp = formUser()

    # figure out what the user specifically wants
    # possible options: [debug, make sprites, new game features, exit]
    def interpret(self, resp):
        


        return 



    # parse the categories to associate relevant words 
    def readCategories(self):
        self.keywords = {}
        catTxt = open("categories.txt", "r").readlines()
        cat = ""
        for line in catTxt:
            line = line.strip()
            if line == "":
                continue
            #new category
            if line[0] == "#":
                cat = line[2:]
                if cat not in self.categories:
                    self.keywords[cat] = []
            #new word
            if line[0] == "+":
                word = line[2:]
                self.keywords[cat].append(word)
            
    # save a new word to the keywords dictionary
    def addNewWord(self, word, category):
        self.keywords[category].append(word)

    #add a new category to the keywords dictionary
    def addNewCategory(self, category):
        self.keywords[category] = []



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
