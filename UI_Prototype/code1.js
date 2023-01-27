//---- GENERAL CODE FOR THE PROTO1.HTML PAGE ----//
// Written by Milk



/////////////   BMO ICON SETUP    //////////////

//icon canvas
var bmo_icon_canvas = document.getElementById("bmo-icon");
bmo_icon_canvas.width = 25;
bmo_icon_canvas.height = 25;
var bitx = bmo_icon_canvas.getContext("2d");

//bmo icon spritesheet setup
let bmo_icon_ss = new Image();
bmo_icon_ss.src = "../data/imgs/bmo_icon.png";
bmo_icon_key = ["awake","sleep","off","think","question","notify","bad","good"]
let icon_size = 16;

var bmo_mode = "idle";

////////////    EDITOR SETUP    //////////////


var game_viewer = document.getElementById("game-viewer");


//ace code editor setup
var ace_editor = ace.edit("ace-code");
ace_editor.setTheme("ace/theme/monokai");  //change to a bluer theme if possible
ace_editor.session.setMode("ace/mode/javascript");
ace_editor.setOptions({
    wrap:true
});
ace_editor.setShowPrintMargin(false); //hides the annoying vertical line


////////////    BMO FACE SETUP    //////////////

// bmo's face for the chat window
var bmo_face_canvas = document.getElementById("bmo-face");
bmo_face_canvas.width = 280;
bmo_face_canvas.height = 175;
var bftx = bmo_face_canvas.getContext("2d");

//sprite sheet bmo face
var bmo_face_ss = new Image();
bmo_face_ss.src = "../data/imgs/bmo_sprite_sheet.png";
let face_width = 800;
let face_height = 606;
let faces_per_row = 9;
let expressions = [
    ["content","huh", "neutral", "sus", "D:", "skeptical", "oh", "sound", ":)"],
    ["-_-", ">:(", "look", "hmm", "confused", "scared", ":(", "OH", "ugh"],
    ["5min", "u", "happy", ":D", "smile", "challenge", "annoyed", "transparent", "noface"]
]


//default bmo face
var bmo_face = new Image();
bmo_face.src = "../data/imgs/bmo_blank.png";



////////////    CHATBOX SETUP    //////////////

let chatbox = document.getElementById("chatbox");



////////////    FUNCTIONS    //////////////


// - icon functions - //

//change the current icon from the spreadsheet
function showIcon(mood){
    // let imsize = icon_size;
    let imsize = bmo_icon_canvas.width;
    let xi = bmo_icon_canvas.width/2 - imsize/2;
    let yi = bmo_icon_canvas.height/2 - imsize/2;

    bitx.clearRect(0,0,bmo_icon_canvas.width,bmo_icon_canvas.height);
    bitx.drawImage(bmo_icon_ss, 
        bmo_icon_key.indexOf(mood)*icon_size, 0, icon_size, icon_size, 
        xi, yi, imsize, imsize);
}

//show or hide the bmo chat sidebar
function toggleChat(){
    let chat_window = document.getElementById("right-half");
    let editor_window = document.getElementById("editor");
    
    //show the window
    if (chat_window.style.display == "none"){
        chat_window.style.display = "block";
        showIcon("awake");
        editor_window.style.width = "620px";
    } 
    //hide the window
    else {
        chat_window.style.display = "none";
        showIcon("off");
        editor_window.style.width = "900px";
    }

    ace_editor.resize()  //resize the code editor
}




// - face functions - //

//return the row and column index of the face in the sprite sheet
function getFace(mood){
    for (let i = 0; i < expressions.length; i++){
        for (let j = 0; j < expressions[i].length; j++){
            if (expressions[i][j] == mood){
                return [i,j]
            }
        }
    }
    return [-1, -1] //if the mood is not found
}

//draw the face of BMO based on the mood given
function drawBMOFace(mood){
    //add background
    bftx.fillStyle = "#4CAA98";
    bftx.fillRect(0, 0, 280, 175);

    //draw the face
    let face = getFace(mood);
    if(face == [-1, -1]){
        console.log(`Mood ${mood} not found!`)
        face = [8,8]; //if the mood is not found, draw the nothing face
    }
    let x = face[1]*face_width;
    let y = face[0]*face_height;
    bftx.drawImage(bmo_face_ss, x, y, face_width, face_height, 0, 0, 280, 175);

    //draw a border around
    bftx.strokeStyle = "#4CAA98";
    bftx.lineWidth = 30;
    bftx.beginPath();
    bftx.roundRect(0, 0, 280, 175,[40]);
    bftx.stroke();

    bftx.strokeStyle = "#000"
    bftx.lineWidth = 2;
    bftx.beginPath();
    bftx.roundRect(14, 13, 250, 146, 25);
    bftx.stroke();

}

// //set default bmo face
// bmo_face.onload = function(){
//     //add background
//     bftx.fillStyle = "#4CAA98";
//     bftx.fillRect(0, 0, 280, 175);

//     //draw the face
//     bftx.drawImage(bmo_face, 0, 0, bmo_face.width, bmo_face.height, 0, 0, 280, 175);

//     //draw a border around
//     bftx.strokeStyle = "#4CAA98";
//     bftx.lineWidth = 30;
//     bftx.beginPath();
//     bftx.roundRect(0, 0, 280, 175,[40]);
//     bftx.stroke();

//     bftx.strokeStyle = "#000"
//     bftx.lineWidth = 2;
//     bftx.beginPath();
//     bftx.roundRect(14, 13, 250, 146, 25);
//     bftx.stroke();

// }

// - chat functions - //

//basic chatbox function
chatbox.addEventListener("keyup", function(event){
    if(event.key == "Enter"){
        console.log("enter pressed");
        let chat_out = document.getElementById("chat-out");
        let chatbox = document.getElementById("chatbox");
        let chatbox_text = chatbox.value;
        chatbox.value = "";
        chat_out.innerHTML += chatbox_text + "<br>";
        chat_out.scrollTop = chat_out.scrollHeight;

        // simple bmo user input
        let {txt, action, face} = bmo.talk(chatbox_text)
        chat_out.innerHTML += txt + "<br>"; 
        drawBMOFace(face);


        /// DEBUGGING IN THE CHAT ///
        //change bmo's face to the input if a keyword is found
        if(chatbox_text.includes("mood: ")){
            let new_mood = chatbox_text.replace("mood: ", "");
            console.log(`new mood: ${new_mood}`)
            drawBMOFace(new_mood);
        }
    }
});


// - editor functions - //

//change which screen the editor window shows
function changeEditorView(modeTab){
    let mode = modeTab.innerHTML.toLowerCase();

    //hide all the other windows and unselect tabs
    let all_windows = document.getElementsByClassName("editor-window");
    for (let i = 0; i < all_windows.length; i++){
        all_windows[i].style.display = "none";
    }
    let all_tabs = document.getElementsByClassName("tool-item-right");
    for (let i = 0; i < all_tabs.length; i++){
        all_tabs[i].classList.remove("tool-select");
    }


    //show the selected window and tab
    let selected_window = document.getElementById(mode + "-editor");
    selected_window.style.display = "block";
    modeTab.classList.add("tool-select");

}


/////// bmo code, TODO: move to a separate file ///////
// needs to be served using a server to work


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
let bmo = new BMO(true);

//initialization function
function init(){
    //set the default icon
    let bmo_shown = document.getElementById("right-half");
    showIcon((bmo_shown.style.display == "block" ? "off" : "awake"));

    //set bmo's face
    drawBMOFace(":)");

    //set some sample code
    ace_editor.setValue("//BMO CODE \
    \nlet bmo = 'cool';\
    \nconsole.log('bmo is ' + bmo);\
    \n\nfunction make_a_game(){\
    \n\treturn 'who wants to play video games?';\
    \n}\
    \nconsole.log(make_a_game());\
    \n\nlet foo = 'If I push this button, you will both be \
dangerously transported into my main brain game frame, \
where it is very dangerous'\
    ",-1);
    ace_editor.clearSelection();

}