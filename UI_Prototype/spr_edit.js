// SPRITE EDITOR CODE 
// Written by Milk

var PALETTE = ["#FFF","#595959","#B1F702","#000"] //offset by 1 (0 is transparent)
var TRANS_COLOR = "#dedede";
var CUR_COLOR = 4;

var TOOLS = {0:'pencil', 1:'paint', 2:'move', 3:'select', 6:'undo', 7:'redo'}
var CUR_TOOL = 0;

var HISTORY = []; 
var MAX_HISTORY = 50;
var REDO_SET = [];

var SPRITES = []; // array of sprites (8x8 int values)
var SPR_INDEX = 0; // index of current sprite in editor
var NAMES = []; // array of sprite names

var EDITOR = null; // editor object
var ETX = null; // editor context
var PREVIEW = null; // preview object
var PTX = null; // preview context
var SPRITE_SHEET = null; // sprite sheet object
var SSTX = null; // sprite sheet context
var WINDOW_SIZE = "small";



////////////    SITE UI / RENDER FUNCTIONS    //////////////


// initialization function called on the start of the page
function init(){
    //set editor size
    // document.getElementById("editor-small").style.display = "block";
    // document.getElementById("editor-wide").style.display = "none";
    WINDOW_SIZE = "wide";
    document.getElementById("editor-"+WINDOW_SIZE).style.display = "block";

    //set up canvases
    EDITOR = document.getElementById("paint-canvas-"+WINDOW_SIZE)
    ETX = EDITOR.getContext("2d");
    EDITOR.width = 320;
    EDITOR.height = 320;

    PREVIEW = document.getElementById("preview-canv");
    PTX = PREVIEW.getContext("2d");
    PREVIEW.width = 64;
    PREVIEW.height = 64;

    SPRITE_SHEET = document.getElementById("ss_canv");
    SSTX = SPRITE_SHEET.getContext("2d");
    SPRITE_SHEET.width = 256;
    SPRITE_SHEET.height = 256;

    //add tools and palette
    addPalette();
    addSpriteList();
    setDemoSprites();

    //set up editor
    showSprite();
    changeTool(0);
    CUR_COLOR = 0;
    makeHistory();

    renderFullSheet();

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


    //to small
    if(WINDOW_SIZE == "wide"){
        content.style.width = "600px";
        document.getElementById("editor-small").style.display = "block";
        document.getElementById("editor-wide").style.display = "none";
        WINDOW_SIZE = "small";
        document.getElementById("spritesheet").style.display = "none";
    }
    //to wide
    else{
        content.style.width = "900px";
        document.getElementById("editor-small").style.display = "none";
        document.getElementById("editor-wide").style.display = "block";
        WINDOW_SIZE = "wide";
        document.getElementById("spritesheet").style.display = "block";
    }

    //reset canvas
    EDITOR = document.getElementById("paint-canvas-"+WINDOW_SIZE);
    ETX = EDITOR.getContext("2d");
    let size = (WINDOW_SIZE == "small") ? 320 : 240;
    EDITOR.width = size;
    EDITOR.height = size;

    //reset tools
    showSprite();
    changeTool(CUR_TOOL);
    setColor(document.getElementById("color-"+CUR_COLOR+"-"+WINDOW_SIZE),CUR_COLOR)();

    showSprite();
    
}

function changeSize(){
    console.log("new size!")
    var content = document.getElementById("content");
    if(content.style.width == "900px"){
        content.style.width = "600px";
        document.getElementById("spritesheet").style.display = "none";
    }else{
        content.style.width = "900px";
        document.getElementById("spritesheet").style.display = "block";
    }
}


// add palette to the palette bar
function addPalette(){
    for(let s=0; s<2; s++){
        let cur_size = (s==0) ? "small" : "wide";
        var palette = document.getElementById("palette-"+cur_size);

        //add the transparent color
        var tr_color = document.createElement("div");
        tr_color.classList.add("palette-item-tr");
        tr_color.style.backgroundColor = TRANS_COLOR;
        if(cur_size == "small")
            tr_color.style.marginBottom = "20px";
        else
            tr_color.style.marginRight = "35px";
        tr_color.onclick = setColor(tr_color,0);
        tr_color.id = "color-0-"+cur_size;
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
            color.id = "color-"+(i+1)+"-"+cur_size;
            palette.appendChild(color);
        }
    }
}

// add sprite list to the sprite list bar
function addSpriteList(){
    // for(let s=0; s<2; s++){
        // let cur_size = (s==0) ? "small" : "wide";
    let cur_size = "small";
    var spriteList = document.getElementById("sprite-list-"+cur_size);
    for(var i=0; i<7; i++){
        var sprite = document.createElement("img");
        sprite.classList.add("spr-item");
        sprite.style.backgroundColor = TRANS_COLOR;
        sprite.onclick = onSprite(i);
        sprite.id = "sprite-"+i+"-"+cur_size;

        spriteList.appendChild(sprite);
    }
    // }
}

// next sprite in list
function nextSprite(){
    makeHistory();
    updateSheetSprite(SPR_INDEX);

    if(SPR_INDEX < SPRITES.length-1)
        SPR_INDEX++;
    else
        SPR_INDEX = 0;
    showSprite();
    activeSheet();
}
// previous sprite in list
function prevSprite(){
    makeHistory();
    updateSheetSprite(SPR_INDEX);
    if(SPR_INDEX > 0)
        SPR_INDEX--;
    else
        SPR_INDEX = SPRITES.length-1;
    showSprite();
    activeSheet();
}

//if the sprite list is clicked, jump to the sprite
function onSprite(index){
    return function(){
        makeHistory();
        updateSheetSprite(SPR_INDEX);
        let lb = Math.max(0,Math.min(SPRITES.length-7,SPR_INDEX-3))
        // console.log("on sprite: " + (index+lb));
        SPR_INDEX = index+lb;
        
        showSprite();
        activeSheet();
    }
}

//jump to an index
function toSprite(d){
    let index = Math.max(Math.min(parseInt(d.value-1), 255),0);

    //hide again
    d.style.display = "none";
    document.getElementById("spr_index-"+WINDOW_SIZE).style.display = "block";

    document.getElementById("spr_index-"+WINDOW_SIZE).innerHTML = (index+1) + " / 256";
    makeHistory();
    SPR_INDEX = index;
    showSprite();
}

//show the input text
function editIndex(){
    let i = document.getElementById("ind_in-"+WINDOW_SIZE);
    document.getElementById("spr_index-"+WINDOW_SIZE).style.display = "none";
    i.value = "";
    i.style.display = "block";
    i.focus();

}


// show sprite in the canvas
function showSprite(){
    //update index value and name
    document.getElementById("spr_index-"+WINDOW_SIZE).innerHTML = (SPR_INDEX+1) + " / 256";
    document.getElementById("sprite-label-"+WINDOW_SIZE).value = NAMES[SPR_INDEX];

    //update the list set
    if(WINDOW_SIZE == "small"){
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
    }
   

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
    for(var i=0;i<3; i++){
        var tool = document.getElementById("tool"+i+"-"+WINDOW_SIZE);
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


//render full spritesheet
function renderFullSheet(){
    let sprx = SPRITE_SHEET.width / 16; //assume square canvas
    let px = sprx / 8;  //assume square sprite

    SSTX.clearRect(0, 0, SPRITE_SHEET.width, SPRITE_SHEET.height);

     //clear and draw transparency color
     SSTX.clearRect(0, 0, SPRITE_SHEET.width, SPRITE_SHEET.height);
     SSTX.fillStyle = TRANS_COLOR;
     SSTX.fillRect(0, 0, SPRITE_SHEET.width, SPRITE_SHEET.height);
     
     

    for(let i=0;i<SPRITES.length;i++){
        let c = i % 16; //columns
        let r = Math.floor(i / 16); //rows
        let cur_spr = SPRITES[i];
        
        for(var j = 0; j < 64; j++){
            let x = j % 8;
            let y = Math.floor(j / 8);
    
            //draw nothing
            if(cur_spr[j] == 0)
                continue;
    
            //draw the color
            var color = PALETTE[cur_spr[j]-1];
            SSTX.fillStyle = color;
            SSTX.fillRect(c*sprx + x*px, r*sprx + y*px, px, px);
        }
    }

    activeSheet();
}

//update a sprite in the spritesheet
function updateSheetSprite(ind){
    let sprx = SPRITE_SHEET.width / 16; //assume square canvas
    let px = sprx / 8;  //assume square sprite

    let c = ind % 16; //columns
    let r = Math.floor(ind / 16); //rows
    let cur_spr = SPRITES[ind];
    
    for(var j = 0; j < 64; j++){
        let x = j % 8;
        let y = Math.floor(j / 8);

        //draw the color
        if(cur_spr[j] != 0){
            var color = PALETTE[cur_spr[j]-1];
            SSTX.fillStyle = color;
        }else{
            SSTX.fillStyle = TRANS_COLOR;
        }
        SSTX.fillRect(c*sprx + x*px, r*sprx + y*px, px, px);
    }
}

//hover over the spritesheet
function hoverSheet(){

}

//draw a box around the current sprite
function activeSheet(){
    let sprx = SPRITE_SHEET.width / 16; //assume square canvas

    let c = SPR_INDEX % 16; //columns
    let r = Math.floor(SPR_INDEX / 16); //rows

    SSTX.strokeStyle = "#00f0ff";
    SSTX.lineWidth = 1;
    SSTX.strokeRect(c*sprx+1, r*sprx+1, sprx-2, sprx-2);
}

//////////////////////      PAINT FUNCTIONS     //////////////////////


var mouseIsDown = false;

// returns offset values for mouse or touch event
function getCursorOffset(e){
    let curs = {offx:0,offy:0};
    //mouse
    if(e instanceof MouseEvent){	
        curs.offx = e.offsetX+3
        curs.offy = e.offsetY+3
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

        //add to history
        makeHistory();
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

    sprOnCanvas();

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
        // console.log("dx: "+dx+" dy: "+dy)

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
    // console.log(queue);
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


// ADDS TO THE HISTORY SET OF LAST MAP ACTION
function makeHistory(){
    let cur_spr = SPRITES[SPR_INDEX];
    let hpt = {spr:[...cur_spr],i:SPR_INDEX};

    //same action as last time
    if(HISTORY.length > 0){
        let lastPt = HISTORY[HISTORY.length-1];
        if(lastPt.spr.toString() === cur_spr.toString() && lastPt.i == SPR_INDEX)
            return;
    }

	//add to the history and remove top if maxed out
	HISTORY.push(hpt);
	if(HISTORY.length > MAX_HISTORY)
		HISTORY.shift(0);

	REDO_SET = [];	//reset the redo list (can no longer redo after this point)
}

// UNDOES THE LAST ACTION TO THE PREVIOUS MAP LAYOUT
function undo(){
	if(HISTORY.length < 1)
		return;

    //add current state to redo list
    let cur_spr = SPRITES[SPR_INDEX];
    let hpt = {spr:[...cur_spr],i:SPR_INDEX};
    REDO_SET.push(hpt);		//add to the redo set

	//set the map
    let lastPt = HISTORY.pop();		//pop off the last element of the history
    SPRITES[lastPt.i] = [...lastPt.spr];
    SPR_INDEX = lastPt.i;
    showSprite(SPR_INDEX);
	
    
	// resetLasso();  			//deselect lasso in case it's out

    // console.log("undo")
}

// REDOES THE LAST ACTION TO THE NEXT MAP LAYOUT
function redo(){
	if(REDO_SET.length == 0)
		return;

    //add to the history and remove top if maxed out
    let cur_spr = SPRITES[SPR_INDEX];
    let hpt = {spr:[...cur_spr],i:SPR_INDEX};
	HISTORY.push(hpt);
	if(HISTORY.length > MAX_HISTORY)
		HISTORY.shift(0);

    //pop from redo list and set
    let redoPt = REDO_SET.pop();
    SPRITES[redoPt.i] = redoPt.spr;
    SPR_INDEX = redoPt.i;
    showSprite(SPR_INDEX);

    // console.log("redo")

	// resetLasso();  			//deselect lasso in case it's out
	
}


///////////////     TEST AND DEBUG     //////////////////



// set demo sprites (8x8 int values)
// to get this from Piskel, goto File > Export as > Other > C file (.c)
// then open and convert all of the hex values to int associated by the palette
function setDemoSprites(){

    //reset globals
    SPRITES = [];
    NAMES = [];

    //add blank sprites
    for(let i=0;i<256;i++){
        let spr = [];
        for(let j=0;j<64;j++)
            spr.push(0);
        SPRITES.push(spr);

        NAMES.push("");
    }

    //set the first x sprites to the demo sprites

    //assume 8x8 sprites
    let demo_sprites = [
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
    let demo_names = ["quaso", "sword", "wall", "alice", "bob", "alien", "cat", "ghost", "ghoul", "computer"]

    //assign the demo sprites/names to the global arrays
    for(let i = 0; i < demo_sprites.length; i++){
        SPRITES[i] = demo_sprites[i];
        NAMES[i] = demo_names[i];
    }
    
}   



let debug = document.getElementById("debug");

function update(){
    requestAnimationFrame(update);

    if (UNIV_PD != null)
        debug.innerHTML = `mouse pos (${UNIV_PD.x}, ${UNIV_PD.y}) | ${mouseIsDown} | touch pt (${touchPt.x}, ${touchPt.y})`
}
update();



///////////////     KEY PRESS SHORTCUTS     //////////////////

//key up (enter) to switch to sprite
document.getElementById("ind_in-"+WINDOW_SIZE).addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        toSprite(this);
    }
});

//check for shortcut
document.addEventListener("keydown", function(event) {
    //undo and redo with ctrl+z and ctrl+y
    if (event.key == "z" && event.ctrlKey) {
        event.preventDefault();
        undo();
    }
    if (event.key == "y" && event.ctrlKey) {
        event.preventDefault();
        redo();
    }
    
    //switch tool
    if (event.key == "p") {
        event.preventDefault();
        changeTool(0);
    }
    else if (event.key == "b") {
        event.preventDefault();
        changeTool(1);
    }
    else if (event.key == "m") {
        event.preventDefault();
        changeTool(2);
    }
});