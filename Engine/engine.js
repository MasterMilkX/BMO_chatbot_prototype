// GENERAL VARIABLES

var GAME_CANVAS = document.getElementById("game");
GAME_CANVAS.width = 128;
GAME_CANVAS.height = 128;

var GAME_CTX = GAME_CANVAS.getContext("2d");
GAME_CTX.imageSmoothingEnabled = false;
GAME_CTX.textRendering = "geometricPrecision";

// ENGINE VARIABLES

var ENGINE = {
    bgColor : "#000000",  // background color
    pal : [               // color palette
        "#000000",        // 0
        "#1D2B53",        // 1
        "#7E2553",        // 2
        "#008751",        // 3
    ]

}

// PARSER FUNCTIONS 
// - inspired by JUNO engine (https://github.com/digitsensitive/juno) and PICO-8 (https://www.lexaloffle.com/pico-8.php)

/**
 * Clear the screen with the background color
 */
function cls(){
    GAME_CTX.fillStyle = ENGINE.bgColor;
    GAME_CTX.fillRect(0, 0, GAME_CANVAS.width, GAME_CANVAS.height);
}

/** 
* Draw a pixel
* @param {number} x - x position
* @param {number} y - y position
* @param {string} c - color index 
*/
function pix(x,y,c){
    GAME_CTX.fillStyle = c;
    GAME_CTX.fillRect(x, y, 1,1);
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

    GAME_CTX.fillStyle = c;
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
    GAME_CTX.fillStyle = c;
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

    GAME_CTX.fillStyle = c;
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

    GAME_CTX.fillStyle = c;

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

    GAME_CTX.fillStyle = c;

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
    GAME_CTX.fillStyle = c;
    GAME_CTX.font = "6px tom-thumb";
    GAME_CTX.textAlign = align;
    GAME_CTX.fillText(t,x,y);
}


// Get pixel color index from 2D position
function pget(){

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


// Get a random number between min and max value
function rnd(){

}


// Simple circle-rectangle-collision.
function crc(){

}


// Simple rectangle-rectangle collision
function rrc(){

}




// ENGINE FUNCTIONS

// RENDER ONTO THE CANVAS
function render(){
    cls();

    pix(32,32,"#f00");
    rect(64,32,6,9,"#0f0");
    rectb(96,32,6,9,"#00f");

    line(32,64,32,72,"#f00");
    circ(64,64,9,"#0f0");
    circb(96,64,9,"#00f");

    txt("Hello World!", 64, 12, "#fff",'center');
    txt("Hi- I'm BMO the game design bot", 2, 20, "#fff");

    
}

// UPDATE THE GAME
function update(){
    render();
    requestAnimationFrame(update);
}


update();

