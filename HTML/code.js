// JAVASCRIPT CODE FOR THE BMO-CHATBOT GAME DESIGNER WEB APP
// Written by Milk

// BMO's face
var bmo_face_canvas = document.getElementById('bmo-face');
var bftx = bmo_face_canvas.getContext('2d');
bmo_face_canvas.width = 300;
bmo_face_canvas.height = 200;

// Chat area output
var chat_area_canvas = document.getElementById('chat-display');
var catx = chat_area_canvas.getContext('2d');


/////  BMO VARIABLES  /////

//import the bmo face expressions
var BMO_face = {
    face : ":)"
}
var expressions = ["pleased","shock",":|","sus","D:",":/",":o","sound",":)","lose","","meh",">:(",":o look","-.-","scared",":|2",":(",":O","?","back_in_5",".u."]
var exp_img = []


//////////////      RENDER AREA     //////////////


// render BMO's face into the canvas
function renderBMO(){
    bftx.clearRect(0, 0, bmo_face_canvas.width, bmo_face_canvas.height);
    bftx.drawImage(exp_img[expressions.indexOf(BMO_face.face)], 0, 0);
}

//render the text from the chat
function renderChat(){
    catx.clearRect(0, 0, chat_area_canvas.width, chat_area_canvas.height);
    catx.fillStyle = "#000";
    catx.fillRect(0, 0, chat_area_canvas.width, chat_area_canvas.height);
    catx.font = "20px Arial";
    catx.fillStyle = "#fff";
    catx.fillText("Hello World",10,50);
}


// central render function
function render(){
    renderBMO();
}


//////////////     EXECUTIVE LOOP     //////////////

//initializing function
function init(){
    //import the expressions
    for (var i = 0; i < expressions.length; i++) {
        if (i==11) continue;  //no expression 11
        exp_img[i] = new Image();
        exp_img[i].src = "imgs/bmo" + (i+1) + ".png";
    }
}

//main loop
function main(){
    render();
    requestAnimationFrame(main);
}

main();