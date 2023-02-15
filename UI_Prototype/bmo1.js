/////// bmo code ///////

//////   CHAT VARIABLES   //////

var maxChats = 50;
var userColor = "#fff";
var bmo_color = "#81E5D1"

function chatItem(text,speaker){
    this.text = text;
    this.color = (speaker == "BMO" ? bmo_color : userColor);
    this.speaker = speaker;
}
var chatHistory = [];

//basic chatbox function

function addChat(chatitem){
    //setup new chat item
    var chatDiv = document.getElementById("chat-out");
    var newChat = document.createElement("div");
    newChat.classList.add("chat");
    newChat.classList.add(chatitem.speaker.toLowerCase()+"_chat");

    // add the name
    var speakName = document.createElement("span");
    speakName.innerHTML = chatitem.speaker;
    speakName.classList.add((chatitem.speaker == "BMO" ? "bmo_name" : "user_name"));
    newChat.appendChild(speakName);
    
    // add the text
    var speakText = document.createElement("span");
    speakText.innerHTML = " " + chatitem.text;
    newChat.appendChild(speakText);

    // add the chat to the div
    chatDiv.appendChild(newChat);
    chatDiv.scrollTop = chatDiv.scrollHeight;

    //remove older chats if there are too many
    while(chatDiv.childElementCount > maxChats){
        chatDiv.removeChild(chatDiv.firstChild);
    }
}

let chatbox = document.getElementById("chatbox");

chatbox.addEventListener("keyup", function(event){
    if(event.key == "Enter"){
        console.log("enter pressed");
        let chatbox_text = chatbox.value;
        chatbox.value = "";
        addChat(new chatItem(chatbox_text,"User"));

        // bmo talk
        let {txt, action, face} = bmo.talk(chatbox_text)
        addChat(new chatItem(txt,"BMO"));
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

function sendChatFromButton(button){
    // TODO I feel like getting reply from bmo could be wrapped into a function
    let chatbox_text = button.innerHTML;
    chatbox.value = "";
    addChat(new chatItem(button.innerHTML,"User"));

    // bmo talk 
    let {txt, action, face} = bmo.talk(chatbox_text);
    addChat(new chatItem(txt,"BMO"));
    drawBMOFace(face);
}

//js copy of the python BMO class
class BMO {
    constructor(debug = false) {
        this.DEBUG = debug
        this.debugTxt("Debugging is on")
        this.exitWords = ["bye", "goodbye", "see ya", "see you later", "cya", "later", "quit", "exit"]
        this.introWords = ["hi", "hello", "hey", "yo"]

        this.debugTxt("constructor")
        this.text_mode = "intro"
    }

    debugTxt(txt) {
        if(this.DEBUG){
            console.log(txt)
        }
    }

    //talk function
    talk(user_resp) {

        if (this.introWords.includes(user_resp)) {
           this.text_mode = "intro";
        }

        //intro
        if (this.text_mode === "intro") {
        this.text_mode = "normal";
        return { txt: "Hi there! I'm BMO, the game dev chatbot!\nWhat do you need? I'll do my best to help you out!", action: "", face: ":)" };
    }

        //normal
        else if (this.text_mode === "normal") {
        //check if the user wants to exit
        if (this.exitWords.includes(user_resp)) {
            return { txt: "Bye!", action: "exit", face: ":)" };
        }

        //otherwise, check what user wants
        let category = user_resp.toLowerCase();
        this.debugTxt("user wants: " + category + "\n");

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
        // else {

        //     // this.text_mode = "learn"
        //     return { txt: "I'm sorry, I don't understand...\nIs this related to code debugging, making sprites, or new game features?", action: "", face: ":/" };
        // }

    }

    }
}

let bmo = new BMO(true);
let {txt, action, face} = bmo.talk("");
addChat(new chatItem(txt,"BMO"));