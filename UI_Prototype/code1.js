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
bmo_icon_ss.onload = function(){showIcon("awake")};
bmo_icon_key = ["awake","sleep","off","think","question","notify","bad","good"]
let icon_size = 16;

var bmo_mode = "idle";

////////////    ACE EDITOR SETUP    //////////////

//ace code editor setup
var ace_editor = ace.edit("ace-code");
ace_editor.setTheme("ace/theme/monokai");  //change to a bluer theme if possible
ace_editor.session.setMode("ace/mode/javascript");
ace_editor.setOptions({
    wrap:true
});


////////////    BMO FACE SETUP    //////////////

// bmo's face for the chat window
var bmo_face_canvas = document.getElementById("bmo-face");
bmo_face_canvas.width = 280;
bmo_face_canvas.height = 175;
var bftx = bmo_face_canvas.getContext("2d");
var bmo_face = new Image();
bmo_face.src = "../data/imgs/bmo_blank.png";



////////////    CHATBOX SETUP    //////////////

let chatbox = document.getElementById("chatbox");






////////////    FUNCTIONS    //////////////


// - icon functions - //

//change the current icon from the spreadsheet
function showIcon(mood){
    // let xi = bmo_icon_canvas.width/2 - icon_size/2 - 1;
    // let yi = bmo_icon_canvas.height/2 - icon_size/2 - 1;
    // let imsize = icon_size;

    let xi = 0
    let yi = 0;
    let imsize = bmo_icon_canvas.width-1;

    bitx.clearRect(0,0,bmo_icon_canvas.width,bmo_icon_canvas.height);
    bitx.drawImage(bmo_icon_ss, 
        bmo_icon_key.indexOf(mood)*icon_size, 0, icon_size, icon_size, 
        xi, yi, imsize, imsize);
}

//show or hide the bmo chat sidebar
function togglerChat(){
    let chat_window = document.getElementById("right-half");
    let editor_window = document.getElementById("left-half");
    
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

    ace_editor.resize()
}




// - face functions - //

//set default bmo face
bmo_face.onload = function(){
    //add background
    bftx.fillStyle = "#000";
    // ctx.fillRect(0, 0, 280, 175);

    //draw the face
    bftx.drawImage(bmo_face, 0, 0, bmo_face.width, bmo_face.height, 0, 0, 280, 175);

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
    }
});


//initialization function
function init(){
    //set the default icon
    showIcon("awake");



}