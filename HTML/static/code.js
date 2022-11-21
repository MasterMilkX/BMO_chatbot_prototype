// JAVASCRIPT CODE FOR THE BMO-CHATBOT GAME DESIGNER WEB APP
// Written by Milk

// BMO's face
var bmo_face_canvas = document.getElementById('bmo-face');
var bftx = bmo_face_canvas.getContext('2d');
bmo_face_canvas.width = 300;
bmo_face_canvas.height = 200;

// Chat area output
// var chat_area_canvas = document.getElementById('chat-display');
// var catx = chat_area_canvas.getContext('2d');
// chat_area_canvas.width = 300;
// chat_area_canvas.height = 335;


/////  BMO VARIABLES  /////

//import the bmo face expressions
var BMO= {
    face : ":)",
    font_color : "#81E5D1"
}
var expressions = ["pleased","shock",":|","sus","D:",":/",":o","sound",":)","lose","","meh","","",">:(",":o look","-.-","scared",":|2",":(",":O","?","back_in_5",".u."]
var exp_img = []

var bmo_quotes = ["Who wants to play video games?","Use the combo move!","Check, please","BMO Chop!","You sure drive a hard burger"]


//////   CHAT VARIABLES   //////

var maxChats = 50;
var userColor = "#fff";

function chatItem(text,speaker){
    this.text = text;
    this.color = (speaker == "BMO" ? BMO.font_color : userColor);
    this.speaker = speaker;
}
var chatHistory = [];


//////////////      RENDER AREA     //////////////


// render BMO's face into the canvas
function renderBMO(){
    bftx.clearRect(0, 0, bmo_face_canvas.width, bmo_face_canvas.height);

    if(exp_img.length > 0){
        let fi = expressions.indexOf(BMO.face);
        let curFace = exp_img[fi];
        if(curFace.width > 0)
            bftx.drawImage(curFace, 0, 0, bmo_face_canvas.width, bmo_face_canvas.height);
    }
}

//render the text from the chat
// function renderChat(){
//     //render background
//     catx.clearRect(0, 0, chat_area_canvas.width, chat_area_canvas.height);
//     catx.fillStyle = "#000";
//     catx.fillRect(0, 0, chat_area_canvas.width, chat_area_canvas.height);

//     //render text
//     if(chatHistory.length == 0)
//         return;
    
//     catx.font = fontSize+"px Courier";
//     let maxLines = Math.min(chatHistory.length, Math.floor(chat_area_canvas.height / (fontSize+lineSpace)));
//     for(let i=maxLines;i>0;i--){
//         let line = chatHistory[chatHistory.length - i];
//         catx.fillStyle = line.color;
//         catx.fillText(line.speaker+": "+line.text, 4, (maxLines - i+1) * (fontSize+lineSpace));
//     }
    
// }


// central render function
function render(){
    renderBMO();
    // renderChat();
}


//////////////     EVENT HANDLERS     //////////////

// get user text input to the chatbox
function chat(txtIn){
    var txt = txtIn.value;
    if(txt.length > 0){
        var ci = new chatItem(txt,"User");
        chatHistory.push(ci);
        txtIn.value = "";
        addChat(ci);
    }

    //activate bmo (demo)
    setTimeout(function(){
        var ci = new chatItem(bmo_quotes[Math.floor(Math.random() * bmo_quotes.length)],"BMO");
        chatHistory.push(ci);
        addChat(ci);
    },1000);
}


function sendUserChat(txtIn){
    var txt = txtIn.value;
    if(txt.length > 0){
        var ci = new chatItem(txt,"User");
        chatHistory.push(ci);
        txtIn.value = "";
        addChat(ci);
    }

    console.log(txt)

    $.ajax({ 
        url: '/bot_chat', 
        type: 'POST', 
        data: {"msg": txt},
        success: function(response){ 
            let bmo_out = JSON.parse(response)
            var ci = new chatItem(bmo_out.txt,"BMO");
            chatHistory.push(ci);
            addChat(ci);

            if(bmo_out.face != null){
                BMO.face = bmo_out.face;
                renderBMO();
            }
        } 
    })
}

//add the chat item to the div stream
function addChat(chatitem){
    //setup new chat item
    var chatDiv = document.getElementById("chat-display2");
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


//show or hide the BMO chat area
function toggleBMO(btn){
    //show the side
    var bmo_chat = document.getElementById("bmo-interact");
    if (bmo_chat.style.display == "table-cell"){
        bmo_chat.style.display = "none";
        btn.innerHTML = "Show BMO";
    } else {
        bmo_chat.style.display = "table-cell";
        btn.innerHTML = "Hide BMO";
    }
}

//check chat
userText = document.getElementById('user-chat');
userText.addEventListener('keyup', function onEvent(e) {
    if (e.keyCode === 13) {
        sendUserChat(userText);
        // console.log("got enter");
    }
});



//////////////     EXECUTIVE LOOP     //////////////

//initializing function
function init(){
    //import the expressions
    for (var i = 0; i < expressions.length; i++) {
        if (i==10 ||i==12||i==13||i==23) continue;  //no expression images for these
        exp_img[i] = new Image();
        exp_img[i].src = "static/imgs/bmo" + (i+1) + ".jpeg";
    }

    //scroll to bottom of chat
    var chatDiv = document.getElementById("chat-display2");
    chatDiv.scrollTop = chatDiv.scrollHeight;
}

//main loop
function main(){
    render();
    requestAnimationFrame(main);
}

main();