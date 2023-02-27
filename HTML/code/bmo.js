// basic stop words and punctuation removal, expanding contractions
stopwords = ['i','me','my','myself','we','our','ours','ourselves','you','your','yours','yourself','yourselves','he','him','his','himself','she','her','hers','herself','it','its','itself','they','them','their','theirs','themselves','what','which','who','whom','this','that','these','those','am','is','are','was','were','be','been','being','have','has','had','having','do','does','did','doing','a','an','the','and','but','if','or','because','as','until','while','of','at','by','for','with','about','against','between','into','through','during','before','after','above','below','to','from','up','down','in','out','on','off','over','under','again','further','then','once','here','there','when','where','why','how','all','any','both','each','few','more','most','other','some','such','no','nor','not','only','own','same','so','than','too','very','s','t','can','will','just','don','should','now']

function removePunctuation(str) {
    return(str.split(".").join("").split(",").join("").split("!").join("").split("?").join(""))
}

const contractions = {
  "'ll": " will",
  "'re": " are",
  "'ve": " have",
  "'d": " would",
  "'m": " am",
  "n't": " not"
};

function expandContractions(str) {
  let expandedSentence = str;
  for (let contraction in contractions) {
    expandedSentence = expandedSentence.replace(contraction, contractions[contraction]);
  }
  return expandedSentence;
}

function removeStopwords(str, stopwords) {
    res = []
    words = str.split(' ')
    for(i=0;i<words.length;i++) {
       word_clean = words[i].split(".").join("")
       if(!stopwords.includes(word_clean)) {
           res.push(word_clean)
       }
    }
    return(res.join(' '))
}  

//js copy of the python BMO class
class BMO {
    constructor(debug = false) {
        this.DEBUG = debug
        this.debugTxt("Debugging is on")

        this.saveWords = this.importCategories()
        this.exitWordds = ["bye", "goodbye", "see ya", "see you later", "cya", "later", "quit", "exit"]
        this.extra_stopwords = ["help", "need", "want"]
        this.debugTxt("constructor")
        this.debugTxt(this.saveWords)

        this.text_mode = "intro"
    }

    debugTxt(txt) {
        if(this.DEBUG){
            console.log(txt)
        }
    }
    // parse the category_words file
    importCategories() {
        let saveWords = {}
        let cat = ""
        //read text file line by line
        const file = "category_words.txt"

        fetch(file).then(response => response.text()).then((data) => {

        const allLines = data.split(/\r\n|\n/)

        //go through each line and check for keywords
        allLines.forEach((line) => {
                if (line == "" || line[0] == "#"){}
                else if(line[0] == "$") {
                    cat = line.substring(2, line.length)
                    if (!(cat in saveWords)) {
                        saveWords[cat] = []
                    }
                }
                else if (line[0] == "+") {
                    let word = line.substring(2, line.length)
                    saveWords[cat].push(word)
                }
        });
        })
        this.debugTxt(saveWords)
        return saveWords
    }

    //export the categories to a text file
    exportCategories() {
        let header_comments = "# Puts relevant words into categories \
        \n# Syntax: \
        \n#   # = comment (do not read) \
        \n#   $ = topic header \
        \n#   + = word"

        //write to file
        const fs = require('fs')
        
        // Data which will write in a file.
        let data = header_comments
        for (var key in this.saveWords) {
            data += "\n\n$ " + key
            this.saveWords[key].forEach(word => {
                data += "\n+ " + word
            });
        }
        
        fs.writeFile('category_words.txt', data, (err) => {})
        
    }

    //save a new word to category
    addNewWord(word, category) {
        this.debugTxt(word + " " + category + "\n")
        this.saveWords[category].push(word)
    }

    //add a new category
    addNewCategory(category) {
        this.saveWords[category] = []
    }

    //add more words to a category file
    associateWords(words, category) {
        words.forEach(word => {
            this.addNewWord(word, category)
        });

        this.exportCategories()
    }

    // figure out what the user specifically wants
    // possible options: [debug, make sprites, new game features, exit]
    matchCategory(user_input) {
        this.debugTxt(this.saveWords)
        return this.rawClosestMatch(user_input, this.saveWords)
    }

    // show the BMO message in a format that shows BMO as the speaker
    formBMO(msg) {
        console.log("BMO: " + msg);
    }
    
    // show the user message in a format that shows the user as the speaker
    formUser() {
        //TODO
    }

    //associate a raw user response to the closest matching group
    //  Input:  resp - the raw user response
    //          wgroups - the dictionary of keywords to match against (form str - list of str)
    rawClosestMatch(resp, wgroups) {
        //remove punctuation
        resp = removePunctuation(resp)

        //expand contractions
        resp = expandContractions(resp)

        //remove stopwords
        resp = removeStopwords(resp, [...this.extra_stopwords, ...stopwords])

        //split into words
        let words = resp.split(" ")

        //find the closest match
        let best_match = ""
        let best_match_score = 0
        for (var key in wgroups) {
            let score = 0
            wgroups[key].forEach(word => {
                if(words.includes(word)) {
                    score += 1
                }
            });
            if(score > best_match_score) {
                best_match = key
                best_match_score = score
            }
        }
        if (best_match_score == 0) {
            best_match = "?"
        }
        
        this.debugTxt("Best match: " + best_match)
        return [best_match, words]
    }
    
    //talk function
    talk(user_resp) {

        //intro
        if (this.text_mode === "intro") {
        this.text_mode = "normal";
        return { txt: "Hi there! I'm BMO, the game dev chatbot!\nWhat do you need? I'll do my best to help you out!", action: "", face: ":)" };
    }

        //normal
        else if (this.text_mode === "normal") {
        //check if the user wants to exit
        if (this.exitWordds.includes(user_resp)) {
            return { txt: "Bye!", action: "exit", face: ":)" };
        }

        //otherwise, check what user wants

        let category = this.matchCategory(user_resp)[0] 
        let words = this.matchCategory(user_resp)[1]
        this.debugTxt("user wants: " + category + "\n")

        if (category == "code debug") {
            return { txt: "I can help you debug your code!", action: "debug", face: ":)" };
        }
        else if (category == "make sprites") {
            return { txt: "I can help you make sprites!", action: "sprites", face: ":)" };
        }
        else if (category == "new game features") {
            return { txt: "I can help you come up with new game feature ideas!", action: "new game features", face: ":)" };
        }

        //if no match, ask for clarification
        else {

            this.text_mode = "learn"
            this.last_words = words
            return { txt: "I'm sorry, I don't understand...\nIs this related to code debugging, making sprites, or new game features?", action: "", face: ":)" };
        }

    }

    //learn mode
    else if (this.text_mode === "learn") {
        this.debugTxt("learning: " + words)

        let cat_keywords = {
                    "code debug": ["debug", "debugging", "bug", "bugs", "error", "errors", "fix", "fixing", "code", "programming"],
                    "sprite generation": ["sprite", "sprites", "art", "graphics", "graphic", "image", "images", "picture", "pictures"],
                    "game feature idea": ["feature", "features", "game", "games", "new"]
        }
        let best_cat = this.rawClosestMatch(user_resp, cat_keywords)[0] 
        this.debugTxt("best cat: " + best_cat)

        if (best_cat === "?") {
            this.text_mode = "normal"
            return { txt: "Ok!", action: "", face: ":)" }
        }
        else {
            this.associateWords(this.last_words, best_cat)
            this.text_mode = "normal"
            this.last_words = []
            return { txt: "Ok!", action: "", face: ":)" }
        }
    

    }
    }
}