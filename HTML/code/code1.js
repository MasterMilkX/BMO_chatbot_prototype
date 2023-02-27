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



//initialization function
function CODE_INIT(){
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