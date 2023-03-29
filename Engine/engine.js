// HTML ELEMENT VARIABLES

var GAME_CANVAS = document.getElementById("game");
GAME_CANVAS.width = 128;
GAME_CANVAS.height = 128;

var GAME_CTX = GAME_CANVAS.getContext("2d");
GAME_CTX.imageSmoothingEnabled = false;
GAME_CTX.textRendering = "geometricPrecision";


var debugArea = document.getElementById("debug");

var gameEditor = document.getElementById("editor");

// ENGINE VARIABLES

var ENGINE = {
    pal : [               // color palette
        "#000000",        // 0 ; background
        "#000000",        // 1
        "#1D2B53",        // 2
        "#7E2553",        // 3
        "#008751",        // 4
    ]

}

// ENGINE FUNCTIONS 
// - inspired by JUNO engine (https://github.com/digitsensitive/juno) and PICO-8 (https://www.lexaloffle.com/pico-8.php)

/**
 * Clear the screen with the background color (0th index in palette)
 */
function cls(){
    GAME_CTX.fillStyle = ENGINE.pal[0];
    GAME_CTX.fillRect(0, 0, GAME_CANVAS.width, GAME_CANVAS.height);
}

/**
 * Set the 4 color palette
 * 
 * @param {string[]} pal - array of 5 colors (0th color is background)
 */
function setPal(pal){
    ENGINE.pal = pal;
}

/** 
* Draw a pixel
* @param {number} x - x position
* @param {number} y - y position
* @param {number} c - color index 
*/
function pix(x,y,c){
    GAME_CTX.fillStyle = ENGINE.pal[c];
    GAME_CTX.fillRect(x, y, 1,1);
}

/**
 * Get pixel color index from 2D position
 * @param {*} x  - x position
 * @param {*} y  - y position
 */
function pget(x,y){
    let imgData = GAME_CTX.getImageData(x,y,1,1);
    let data = imgData.data;
    return data[3];
}

/**
 * Draw a line
 * @param {number} x1 - x position of the first point
 * @param {number} y1 - y position of the first point
 * @param {number} x2 - x position of the second point
 * @param {number} y2 - y position of the second point
 * @param {string} c - color index
 * @param {number} l - line width
 */
function line(x1,y1,x2,y2,c,l=1){
    let w = x2-x1;
    let h = y2-y1;
    if (w==0 && h==0)
        return

    GAME_CTX.fillStyle = ENGINE.pal[c];
    GAME_CTX.fillRect(x1, y1, Math.max(1,w), Math.max(1,h));
}

/**
 * Draw a filled rectangle
 * @param {number} x - x position
 * @param {number} y - y position
 * @param {number} w - width
 * @param {number} h - height
 * @param {string} c - color index
 */
function rect(x,y,w,h,c){
    GAME_CTX.fillStyle = ENGINE.pal[c];
    GAME_CTX.fillRect(x, y, w, h);
}

/**
 * Draw a rectangle outline. Fills with transparent color.
 * @param {number} x - x position
 * @param {number} y - y position
 * @param {number} w - width
 * @param {number} h - height
 * @param {string} c - color index
 * @param {number} l - line width
 */
function rectb(x,y,w,h,c,l=1){
    // GAME_CTX.strokeStyle = c;
    // GAME_CTX.lineWidth = l;
    // GAME_CTX.strokeRect(x, y, w, h);

    //top, bottom, left, right borders
    let xs = [x,x,x,x+w-l];
    let ys = [y,y+h-l,y,y];
    let ws = [w-l,w-l,l,l];
    let hs = [l,l,h-l,h];

    GAME_CTX.fillStyle = ENGINE.pal[c];
    for(let i=0; i<4; i++){
        GAME_CTX.fillRect(xs[i], ys[i], ws[i], hs[i]);
    }

}

// Math.floor() but smaller
function mf(i){return Math.floor(i);}

/**
 * Draw a filled circle. Uses the Minsky circle algorithm.
 * @param {number} x - x position
 * @param {number} y - y position
 * @param {number} r - radius
 * @param {string} c - color index
 */
function circ(xc, yc, r, c) {  
    xc=xc+0.5;
    yc=yc+0.5;
    r=r;
    let j = r;
    let k = 0;
    let rat = 1/r;

    GAME_CTX.fillStyle = ENGINE.pal[c];

    for(let i=0; i<r*0.786; i++){
        k -= rat*j
        j += rat*k

        let xs1 = [mf(xc+j), mf(xc-j), mf(xc-k), mf(xc+k)]
        let ys1 = [mf(yc+k), mf(yc+k), mf(yc-j), mf(yc-j)]
        let xs2 = [mf(xc+j), mf(xc-j), mf(xc-k), mf(xc+k)]
        let ys2 = [mf(yc-k), mf(yc-k), mf(yc+j), mf(yc+j)]

        for(let i=0; i<4; i++){
            let w = xs2[i]-xs1[i]+1;
            let h = ys2[i]-ys1[i]+1;
            GAME_CTX.fillRect(xs1[i], ys1[i], w, h);
        }
    }
    GAME_CTX.fillRect(mf(xc),mf(yc-r),1,2*r+1)
}

/**
 * Draw a circle outline. Uses the Minsky circle algorithm.
 * Taken from PICO-8 implementation: https://www.lexaloffle.com/bbs/?pid=44630#p
 * @param {number} xc - x position (center)
 * @param {number} yc - y position (center)
 * @param {number} r - radius
 * @param {string} c - color index
 * @param {number} w - line width
 */
function circb(xc,yc,r,c,w=1){
    xc=xc+0.5;
    yc=yc+0.5;
    r=r;

    let j = r;
    let k = 0;
    let rat = 1/r;

    GAME_CTX.fillStyle = ENGINE.pal[c];

    for(let i=0; i<r*0.785; i++){
    // for(let i=0; i<r*1.618; i++){
        k -= rat*j
        j += rat*k
        GAME_CTX.fillRect(mf(xc+j), mf(yc+k), w, w);
        GAME_CTX.fillRect(mf(xc-j), mf(yc+k), w, w);
        GAME_CTX.fillRect(mf(xc+j), mf(yc-k), w, w);
        GAME_CTX.fillRect(mf(xc-j), mf(yc-k), w, w);
        GAME_CTX.fillRect(mf(xc+k), mf(yc+j), w, w);
        GAME_CTX.fillRect(mf(xc-k), mf(yc+j), w, w);
        GAME_CTX.fillRect(mf(xc+k), mf(yc-j), w, w);
        GAME_CTX.fillRect(mf(xc-k), mf(yc-j), w, w);
    }
    GAME_CTX.fillRect(mf(xc+r), mf(yc), w, w);
    GAME_CTX.fillRect(mf(xc-r), mf(yc), w, w);
    GAME_CTX.fillRect(mf(xc), mf(yc+r), w, w);
    GAME_CTX.fillRect(mf(xc), mf(yc-r), w, w);


    //rounder version
    // xc=xc+0.5;
    // yc=yc+0.5;
    // r=r*0.707108;

    // let j = r;
    // let k = r;
    // let rat = 0.5/r;'

    // for(let i=0; i<r*1.618; i++){
    //     k -= rat*j
    //     j += rat*k
    //     GAME_CTX.fillRect(mf(xc+j), mf(yc+k), w, w);
    //     GAME_CTX.fillRect(mf(xc-j), mf(yc+k), w, w);
    //     GAME_CTX.fillRect(mf(xc+j), mf(yc-k), w, w);
    //     GAME_CTX.fillRect(mf(xc-j), mf(yc-k), w, w);
    //     GAME_CTX.fillRect(mf(xc+k), mf(yc+j), w, w);
    //     GAME_CTX.fillRect(mf(xc-k), mf(yc+j), w, w);
    //     GAME_CTX.fillRect(mf(xc+k), mf(yc-j), w, w);
    //     GAME_CTX.fillRect(mf(xc-k), mf(yc-j), w, w);
    // }

}




// Draw some text

/**
 * Draw some text
 * @param {string} t - text to render
 * @param {number} x - x position
 * @param {number} y - y position
 * @param {string} c - color index
 * @param {string} align - text alignment (left, center, right)
 */
function txt(t,x,y,c,align="left"){
    GAME_CTX.fillStyle = ENGINE.pal[c];
    GAME_CTX.font = "6px tom-thumb";
    GAME_CTX.textAlign = align;
    GAME_CTX.fillText(t,x,y);
}


// Add a sprite
function spr(){

}


// Get map tile index
function mget(){

}


// Set map tile index
function mset(){

}


// Check if a key is currently pressed
function key(){

}


// Check if a key was pressed in the frame before (only once)
function keyp(){

}


// Get the ticks since start of the game
function ticks(){

}

/**
 * Get a random number between 2 floats (default 0 and 1)
 * @param {number} min
 * @param {number} max
 */
function rnd(min=0,max=1){
    return Math.random()*(max-min)+min;
}

/**
 * Get a random number between min and max value (integers)
 * @param {number} min 
 * @param {number} max 
 */
function rndi(min,max){
    return Math.floor(Math.random()*(max-min+1)+min);
}


// Simple circle-rectangle-collision.
function crc(){

}


// Simple rectangle-rectangle collision
function rrc(){

}


// PARSER FUNCTIONS


/**
 * Debug function (shows at the bottom of the screen)
 * @param {string} txt - text to print
 * @param {boolean} reset - reset the debug text
 */
function debug(txt,reset=true){
    if(reset)
        debugArea.innerHTML = "";
    debugArea.innerHTML += txt;
}


/**
 * Parses a text game data file to the game (rewrites to executable JS code)
 * 
 * @param {string} dat - text game data file
 */
function parseDat(dat){

    //pull from the text area if no data is passed
    if(dat == null){
        dat = gameEditor.value;
        debug("Parsing data from text area...\n")
    }

    if(dat == ""){
        debug("No data to parse. Please enter some data in the text area.\n")
        return;
    }


    ////////      use regular expressions to parse/extract code for pure javascript execution     ////////

    /// CONVERT VOCABULARY TO JAVASCRIPT ///

    dat = dat.replace(/--(.*)\n/g, "// $1\n");    // convert all comments
    dat = dat.replace(/\bend\b/g, "}");      //convert ends to closing brackets
    dat = dat.replace(/\bret\b/g, "return");      //convert ret to return

    ///    SPECIAL CONVERSIONS    ///
    
    dat = dat.replace(/^func\s([a-zA-Z_]+\(.*\))/gm, "function $1{");   //convert func to function
    dat = dat.replace(/\)\n/g, ");\n");      // add semicolon
    dat = dat.replace(/(\t|^\s\s+)+/g, "");           // remove tabs

    ///  GET SPECIAL CODE BLOCKS   ///

    //get init function

    //check output
    console.log(dat);
}


// INITIALIZATION FUNCTION
function init(){
    console.clear();  //for the console in dev tools 
}



// RENDER ONTO THE CANVAS
function render(){
    // cls();

    // pix(32,32,"#f00");
    // rect(64,32,6,9,"#0f0");
    // rectb(96,32,6,9,"#00f");

    // line(32,64,32,72,"#f00");
    // circ(64,64,9,"#0f0");
    // circb(96,64,9,"#00f");

    // txt("Hello World!", 64, 12, "#fff",'center');
    // txt("Hi- I'm BMO the game design bot", 2, 20, "#fff");

    
}

// UPDATE THE GAME
function update(){
    render();
    requestAnimationFrame(update);
}


update();

