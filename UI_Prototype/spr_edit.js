// SPRITE EDITOR CODE 
// Written by Milk

var PALETTE = ["#FFF","#595959","#B1F702","#000"] //offset by 1 (0 is transparent)
var TRANS_COLOR = "#dedede";
var CUR_COLOR = 4;

var TOOLS = {0:'pencil', 1:'paint', 2:'move', 3:'select'}
var CUR_TOOL = 0;

var SPRITES = []; // array of sprites (8x8 int values)
var SPR_INDEX = 0; // index of current sprite in editor
var NAMES = []; // array of sprite names

var EDITOR = null; // editor object
var ETX = null; // editor context
var PREVIEW = null; // preview object
var PTX = null; // preview context


var WINDOW_SIZE = "small";

// initialization function called on the start of the page
function init(){
    //set editor size
    document.getElementById("editor-small").style.display = "block";
    document.getElementById("editor-wide").style.display = "none";
    WINDOW_SIZE = "small";

    EDITOR = document.getElementById("paint-canvas-small")
    ETX = EDITOR.getContext("2d");
    EDITOR.width = 320;
    EDITOR.height = 320;

    PREVIEW = document.getElementById("preview-canv");
    PTX = PREVIEW.getContext("2d");
    PREVIEW.width = 64;
    PREVIEW.height = 64;

    //add tools and palette
    addPalette();
    addSpriteList();
    setDemoSprites();
    showSprite();
    changeTool(0);
    CUR_COLOR = 0;

    //mouse function assignments
    document.addEventListener("mousedown", editorDown);
    document.addEventListener("mouseup", editorUp);
    document.addEventListener("mousemove", editorMove);
    document.addEventListener("mouseout", editorLeave)


}

// toggle between small and wide
function toggleSize(){
    console.log("new size!")
    var content = document.getElementById("content");
    if(content.style.width == "900px"){
        content.style.width = "600px";
        document.getElementById("editor-small").style.display = "block";
        document.getElementById("editor-wide").style.display = "none";
        WINDOW_SIZE = "small";
        EDITOR.width = 320;
        EDITOR.height = 320;
    }else{
        content.style.width = "900px";
        document.getElementById("editor-small").style.display = "none";
        document.getElementById("editor-wide").style.display = "block";
        WINDOW_SIZE = "wide";
    }

    EDITOR = document.getElementById("paint-canvas-"+WINDOW_SIZE);
    ETX = EDITOR.getContext("2d");

    //mouse function assignments
    
}


// add palette to the palette bar
function addPalette(){
    var palette = document.getElementById("palette-small");

    //add the transparent color
    var tr_color = document.createElement("div");
    tr_color.classList.add("palette-item-tr");
    tr_color.style.backgroundColor = TRANS_COLOR;
    tr_color.onclick = setColor(tr_color,0);
    tr_color.id = "color-0";
    tr_color.classList.add("sel-pal");
    palette.appendChild(tr_color);


    //add the palette colors
    for(var i=0; i<PALETTE.length; i++){
        var color = document.createElement("div");
        color.classList.add("palette-item");
        color.style.backgroundColor = PALETTE[i];

        //set the color
        color.onclick = setColor(color,i+1);
            
        //set the id + add to palette
        color.id = "color-"+(i+1);
        palette.appendChild(color);
    }
}

// add sprite list to the sprite list bar
function addSpriteList(){
    var spriteList = document.getElementById("sprite-list-small");
    for(var i=0; i<7; i++){
        var sprite = document.createElement("img");
        sprite.classList.add("spr-item");
        sprite.style.backgroundColor = TRANS_COLOR;
        sprite.onclick = onSprite(i);
        sprite.id = "sprite-"+i;

        spriteList.appendChild(sprite);
    }
}

// next sprite in list
function nextSprite(){
    if(SPR_INDEX < SPRITES.length-1)
        SPR_INDEX++;
    showSprite();
}
// previous sprite in list
function prevSprite(){
    if(SPR_INDEX > 0)
        SPR_INDEX--;
    showSprite();
}

//if the sprite list is clicked, jump to the sprite
function onSprite(index){
    return function(){
        let lb = Math.max(0,Math.min(SPRITES.length-7,SPR_INDEX-3))
        // console.log("on sprite: " + (index+lb));
        SPR_INDEX = index+lb;
        showSprite();
    }
}

// show sprite in the canvas
function showSprite(){
    //update index value and name
    document.getElementById("spr_index").innerHTML = (SPR_INDEX+1) + " / 256";
    document.getElementById("sprite-label-"+WINDOW_SIZE).value = NAMES[SPR_INDEX];

    //update the list set
    let spr_imgs = document.getElementById("sprite-list-"+WINDOW_SIZE).getElementsByTagName("img");
    let lb = Math.max(0,Math.min(SPRITES.length-7,SPR_INDEX-3))  // 0 < x < L-7
    for(let i=lb;i<lb+7;i++){
        //draw the sprite in the preview canvas
        sprOnCanvas(PREVIEW, PTX, i);
        spr_imgs[i-lb].src = PREVIEW.toDataURL();
    }

    //change border
    for(let i=0;i<7;i++)
        spr_imgs[i].classList.remove("sel-spr");
    spr_imgs[SPR_INDEX-lb].classList.add("sel-spr");

    //draw in the editor
    sprOnCanvas();
}

// draw in the canvas (specified with canvas and context)
function sprOnCanvas(canv=EDITOR, cont=ETX, ind=SPR_INDEX, cur_spr=null){
    //clear and draw transparency color
    cont.clearRect(0, 0, canv.width, canv.height);
    cont.fillStyle = TRANS_COLOR;
    cont.fillRect(0, 0, canv.width, canv.height);

    //draw the sprite
    if(cur_spr == null)
        cur_spr = SPRITES[ind];  //set to current sprite
    
    let px = canv.width / 8;  //assume square canvas
    for(var i = 0; i < 64; i++){
        let x = i % 8;
        let y = Math.floor(i / 8);

        //draw nothing
        if(cur_spr[i] == 0)
            continue;

        //draw the color
        var color = PALETTE[cur_spr[i]-1];
        cont.fillStyle = color;
        cont.fillRect(x*px, y*px, px, px);
    }
}

// changes the name of the current sprite
function changeSprName(newName){
    NAMES[SPR_INDEX] = newName;
}

// changes the current tool
function changeTool(tool_index){
    //change tool 
    CUR_TOOL = tool_index;
    for(var i=0;i<4; i++){
        var tool = document.getElementById("tool"+i);
        if(i == tool_index)
            tool.classList.add("sel-tool");
        else
            tool.classList.remove("sel-tool");
    }

    //change canvas cursor
    EDITOR.style.cursor = `url('../data/imgs/bmo_cursors/${TOOLS[CUR_TOOL]}.png'), pointer`;

}

// sets the color of the pencil based on the palette
function setColor(div,i){
    return function(){
        CUR_COLOR = i;

        let ch = document.getElementById("palette-"+WINDOW_SIZE).children;
        for(let j=0;j<ch.length;j++)
            ch[j].classList.remove("sel-pal");

        div.classList.add("sel-pal");
        // console.log("color "+i+" selected");
    }
}


//////////////////////      PAINT FUNCTIONS     //////////////////////


var mouseIsDown = false;

// returns offset values for mouse or touch event
function getCursorOffset(e){
    let curs = {offx:0,offy:0};
    //mouse
    if(e instanceof MouseEvent){	
        curs.offx = e.offsetX
        curs.offy = e.offsetY
    }
    //touch
    else{
        let rect = e.target.getBoundingClientRect();
        let ox = e.targetTouches[0].pageX - rect.left;
        let oy = e.targetTouches[0].pageY - rect.top;

        curs.offx = ox;
        curs.offy = oy;
    }
    return curs
}

// when the editor cursor is pressed (mouse or touch)
let touchPt = {x:-1,y:-1};
function editorDown(e){
    //ignore all else
    if(e.target.id != "paint-canvas-"+WINDOW_SIZE)
        return;

    e.preventDefault();
    curs = getCursorOffset(e);

    //add the first touch point
    if(!mouseIsDown){
        let pt = getCursPos(curs);
        touchPt = {x:pt.x,y:pt.y};
    }

    mouseIsDown = true;
    if(mouseIsDown)
		paint(curs);
}

// when the editor cursor is lifted (mouse or touch)
function editorUp(e){
    //ignore all else
    if(e.target.id != "paint-canvas-"+WINDOW_SIZE && new_spr == null)
        return;

    //reset the tool back to up position and set the new sprite position
    if(CUR_TOOL == 2){ 
        EDITOR.style.cursor = `url('../data/imgs/bmo_cursors/${TOOLS[CUR_TOOL]}.png'), pointer`
        SPRITES[SPR_INDEX] = new_spr;
        new_spr = null;
    }

    //reset everything
	e.preventDefault();
	mouseIsDown = false;
    touchPt = {x:-1,y:-1};

    //redraw the sprite in the list
    showSprite();

    ghostPixel(curs);
}	

// when cursor is moved over editor (mouse or touch)
function editorMove(e){
    //ignore all else
    if(e.target.id != "paint-canvas-"+WINDOW_SIZE)
        return;

	e.preventDefault();
	curs = getCursorOffset(e);
	if(mouseIsDown)
		paint(curs);
    else
        ghostPixel(curs);
}

// when the cursor leaves the editor
function editorLeave(e){
    //ignore all else
    if(e.target.id != "paint-canvas-"+WINDOW_SIZE)
        return;

	e.preventDefault();

    //reset everything
    if(new_spr == null){
        mouseIsDown = false;
        touchPt = {x:-1,y:-1};
        sprOnCanvas();
    }
}

// returns the x,y position of the cursor on the editor
function getCursPos(ev){

    let px = EDITOR.width / 8;  //assume square canvas

    //realign cursor coordinates
	var modX = (ev.offx * EDITOR.width) / EDITOR.offsetWidth;
	var modY = (ev.offy * EDITOR.height) / EDITOR.offsetHeight;
	let x = Math.floor(modX / px);  
	let y = Math.floor(modY/ px); 
    let pos = y*8+x;

    return {x:x,y:y,px:px,pos:pos,rx:modX,ry:modY};
}

let UNIV_PD = null;


// show the ghost pixel color when the mouse is over the editor
function ghostPixel(ev){
    let cur_spr = SPRITES[SPR_INDEX];

    let pd = getCursPos(ev);
    UNIV_PD = pd;  //for debugging

    //check for out of bounds
	if(pd.x < 0 || pd.x >= 8)
        return;
    else if(pd.y < 0 || pd.y >= 8)
        return;

    //draw the sprite
    sprOnCanvas();

    //draw the ghost pixel
    if(CUR_TOOL == 0){
        
        if((cur_spr[pd.pos] == 0)){
            //ghost of current pixel color
            if(CUR_COLOR == 0){
                ETX.fillStyle = "#fff";
                ETX.globalAlpha = 0.5;
            }else{
                ETX.fillStyle = PALETTE[CUR_COLOR-1];
                ETX.globalAlpha = 0.6;
            }
        }else{
            ETX.fillStyle = "#000";
            ETX.globalAlpha = 0.3;
        }
        
       /*
        //ghost of white pixel - regardless of set color
        ETX.fillStyle = "#fff";
        ETX.globalAlpha = 0.5;
       */
        ETX.fillRect(pd.x*pd.px, pd.y*pd.px, pd.px, pd.px);
        ETX.globalAlpha = 1;
    }

}



// EDITOR METHOD FOR PAINTING ON SQUARES
let new_spr = null;
function paint(ev){
	// console.log("i like it! picasso!")

    let cur_spr = SPRITES[SPR_INDEX];
	let pd = getCursPos(ev);
    UNIV_PD = pd;  //for debugging

	//check for out of bounds
	if(pd.x < 0 || pd.x >= 8)
        return;
    else if(pd.y < 0 || pd.y >= 8)
        return;

    // sprOnCanvas();

	//draw the pixel
	if(CUR_TOOL == 0){
		//already there
		if(cur_spr[pd.pos] == CUR_COLOR)
			return;

		cur_spr[pd.pos] = CUR_COLOR;
        sprOnCanvas();
	}

    //paint fill
    else if(CUR_TOOL == 1){
        let fill_pts = pixSearch(pd.x,pd.y);
        for(let i=0;i<fill_pts.length;i++){
            let pt = fill_pts[i];
            cur_spr[pt.pos] = CUR_COLOR;
        }
        sprOnCanvas();
        
	}

    //sprite drag
    else if(CUR_TOOL == 2){
        //set the cursor to hold
        EDITOR.style.cursor = `url('../data/imgs/bmo_cursors/hold.png'), pointer`;

        if(touchPt.x == -1 || touchPt.y == -1)
            return;

        let dx = pd.x - touchPt.x;
        let dy = pd.y - touchPt.y;
        console.log("dx: "+dx+" dy: "+dy)

        //move the sprite based on changed position
        new_spr = [];
        for(let i=0;i<cur_spr.length;i++){
            let x = i%8;
            let y = Math.floor(i/8);
            let nx = x-dx;
            let ny = y-dy;
            if(nx < 0 || nx >= 8 || ny < 0 || ny >= 8)
                new_spr[i] = 0;
            else{
                let npos = ny*8+nx;
                new_spr[i] = cur_spr[npos];
            }
        }
        // SPRITES[SPR_INDEX] = new_spr;
        sprOnCanvas(EDITOR,ETX,0,new_spr);
    }
}

// search for similar color pixels from a starting point
// for use with the paint fill tool
function pixSearch(x,y){
    let queue = [];
    let color = [];
    let visited = [];

    let first_pt = {x:x,y:y,pos:y*8+x};
    let cur_spr = SPRITES[SPR_INDEX];
    queue.push(first_pt);
    color.push(first_pt)
    visited.push(first_pt.x+","+first_pt.y);
    let t = 0;
    while(queue.length > 0 && t < 64){
        let pt = queue.pop();
        let ne = neighbors(pt);
        for(let i=0;i<ne.length;i++){
            let n = ne[i];
            let nstr = n.x+","+n.y;
            if(cur_spr[n.pos] == cur_spr[first_pt.pos] && !visited.includes(nstr)){
                queue.push(n);
                color.push(n);
                visited.push(nstr);
            }
        }
        t++;
    }
    console.log(queue);
    return color;
}

//get neighbors of a pixel
function neighbors(pt){
    let n = [];

    let left = {x:pt.x-1,y:pt.y,pos:pt.pos-1};
    let right = {x:pt.x+1,y:pt.y,pos:pt.pos+1};
    let up = {x:pt.x,y:pt.y-1,pos:pt.pos-8};
    let down = {x:pt.x,y:pt.y+1,pos:pt.pos+8};

    if(left.x >= 0)
        n.push(left);
    if(right.x < 8)
        n.push(right);
    if(up.y >= 0)
        n.push(up);
    if(down.y < 8)
        n.push(down);

    return n;
}








// set demo sprites (8x8 int values)
// to get this from Piskel, goto File > Export as > Other > C file (.c)
// then open and convert all of the hex values to int associated by the palette
function setDemoSprites(){

    //assume 8x8 sprites
    SPRITES = [
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 1, 1, 0, 0, 0, 
        0, 0, 1, 1, 1, 1, 0, 0, 
        0, 0, 1, 0, 0, 1, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 1, 0, 0, 0, 0, 
        0, 0, 0, 1, 0, 0, 0, 0, 
        0, 0, 0, 1, 0, 0, 0, 0, 
        0, 0, 0, 1, 0, 0, 0, 0, 
        0, 0, 1, 1, 1, 0, 0, 0, 
        0, 0, 0, 1, 0, 0, 0, 0
        ],
        [
        1, 1, 1, 1, 1, 1, 1, 1, 
        1, 0, 0, 0, 0, 0, 0, 1, 
        1, 0, 1, 1, 1, 1, 0, 1, 
        1, 0, 1, 1, 1, 1, 0, 1, 
        1, 0, 1, 1, 1, 1, 0, 1, 
        1, 0, 1, 1, 1, 1, 0, 1, 
        1, 0, 0, 0, 0, 0, 0, 1, 
        1, 1, 1, 1, 1, 1, 1, 1
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 3, 3, 3, 3, 0, 0, 
        0, 3, 3, 3, 3, 1, 3, 0, 
        0, 3, 3, 3, 1, 4, 1, 0, 
        0, 3, 1, 1, 1, 1, 3, 0, 
        0, 0, 3, 4, 4, 3, 0, 0, 
        0, 0, 0, 2, 2, 0, 0, 0, 
        0, 0, 0, 4, 4, 0, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 4, 4, 4, 4, 0, 0, 
        0, 4, 2, 2, 2, 2, 4, 0, 
        0, 2, 4, 2, 2, 4, 2, 0, 
        0, 0, 2, 2, 2, 2, 0, 0, 
        0, 0, 0, 4, 4, 0, 0, 0, 
        0, 0, 0, 4, 3, 0, 0, 0, 
        0, 0, 0, 3, 3, 0, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 3, 0, 0, 0, 0, 3, 0, 
        0, 0, 3, 3, 3, 3, 0, 0, 
        0, 3, 4, 3, 3, 4, 3, 0, 
        0, 0, 3, 3, 3, 3, 0, 0, 
        0, 0, 0, 4, 1, 0, 0, 0, 
        0, 0, 0, 1, 4, 0, 0, 0, 
        0, 0, 0, 4, 1, 0, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 4, 0, 0, 4, 0, 0, 
        0, 0, 4, 4, 4, 4, 0, 0, 
        0, 0, 3, 4, 4, 3, 0, 0, 
        0, 0, 4, 4, 4, 4, 0, 0, 
        0, 0, 0, 4, 4, 0, 4, 0, 
        0, 0, 0, 4, 4, 4, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 1, 1, 0, 0, 0, 
        0, 0, 1, 1, 1, 1, 0, 0, 
        0, 0, 4, 1, 1, 4, 0, 0, 
        0, 0, 1, 1, 1, 1, 0, 0, 
        0, 0, 1, 0, 0, 1, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 0, 0, 1, 1, 1, 1, 0, 
        0, 1, 1, 1, 4, 4, 4, 0, 
        0, 0, 1, 4, 3, 4, 3, 0, 
        0, 0, 0, 1, 1, 1, 1, 0, 
        0, 0, 0, 0, 1, 1, 0, 0, 
        0, 0, 1, 1, 1, 1, 0, 0
        ],
        [
        0, 0, 0, 0, 0, 0, 0, 0, 
        0, 1, 1, 1, 1, 1, 2, 0, 
        0, 1, 3, 4, 4, 1, 2, 0, 
        0, 1, 4, 4, 4, 1, 2, 0, 
        0, 1, 1, 1, 1, 1, 2, 0, 
        0, 0, 0, 2, 2, 0, 0, 0, 
        0, 0, 1, 1, 1, 1, 0, 0, 
        0, 1, 1, 1, 1, 1, 1, 0
        ]
    ];

    NAMES = ["quaso", "sword", "wall", "alice", "bob", "alien", "cat", "ghost", "ghoul", "computer"]
}   


///////////////     DEBUG     //////////////////


let debug = document.getElementById("debug");

function update(){
    requestAnimationFrame(update);

    if (UNIV_PD != null)
        debug.innerHTML = `mouse pos (${UNIV_PD.x}, ${UNIV_PD.y}) | ${mouseIsDown} | touch pt (${touchPt.x}, ${touchPt.y})`
}
update();