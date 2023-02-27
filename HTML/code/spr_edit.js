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

var PICK_IND = 0;

var EDITOR = null; // editor object
var ETX = null; // editor context
var PREVIEW = null; // preview object
var PTX = null; // preview context
var WINDOW_SIZE = "small";



////////////    SITE UI / RENDER FUNCTIONS    //////////////


// initialization function called on the start of the page
function SPRITE_INIT(){

    //set editor size
    // document.getElementById("spr-editor-small").style.display = "block";
    // document.getElementById("spr-editor-wide").style.display = "none";
    document.getElementById("spr-editor-"+WINDOW_SIZE).style.display = "block";

    //set up canvases
    EDITOR = document.getElementById("paint-canvas-"+WINDOW_SIZE)
    ETX = EDITOR.getContext("2d");
    EDITOR.width = 320;
    EDITOR.height = 320;

    PREVIEW = document.getElementById("preview-canv");
    PTX = PREVIEW.getContext("2d");
    PREVIEW.width = 64;
    PREVIEW.height = 64;

    //set up sprites
    setDemoSprites();

    //add tools and palette
    addPalette();
    addSpriteList();
    addSpriteSheet();

    //set up editor
    showSprite();
    changeTool(0);
    CUR_COLOR = 0;
    makeHistory();


    //mouse function assignments
    document.addEventListener("mousedown", editorDown);
    document.addEventListener("mouseup", editorUp);
    document.addEventListener("mousemove", editorMove);
    document.addEventListener("mouseout", editorLeave)

    WINDOW_SIZE = (WINDOW_SIZE == "wide") ? "small" : "wide";
    toggleSize();


}

// toggle between small and wide
function toggleSize(){
    console.log("new size!")
    var content = document.getElementById("content");


    //to small
    if(WINDOW_SIZE == "wide"){
        if(content)
            content.style.width = "600px";
        document.getElementById("spr-editor-small").style.display = "block";
        document.getElementById("spr-editor-wide").style.display = "none";
        WINDOW_SIZE = "small";
        document.getElementById("spritesheet").style.display = "none";
    }
    //to wide
    else{
        if(content)
            content.style.width = "900px";
        document.getElementById("spr-editor-small").style.display = "none";
        document.getElementById("spr-editor-wide").style.display = "block";
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
    changeTool(CUR_TOOL);
    setColor(document.getElementById("color-"+CUR_COLOR+"-"+WINDOW_SIZE),CUR_COLOR)();
    showSprite();
    setAllPalPos();
    
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

        // let x = parseInt(tr_color.offsetLeft)
        // let y = parseInt(tr_color.offsetTop)

        // let offx = (cur_size == "wide") ? 25 : -25;
        // let offy = (cur_size == "wide") ? 60 : 13;

        // console.log(cur_size + "-0: (" + x + ", " + y+")");
        // tr_color.ondblclick = gotoPalette(0,x+(offx),y+(offy));


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

            //set the position
            // let x = parseInt(color.offsetLeft)
            // let y = parseInt(color.offsetTop)
            // console.log(cur_size + "-"+(i+1)+": (" + x + ", " + y+")");
            // color.ondblclick = gotoPalette(i+1,x+offx,y+offy);
        }
    }
}

// set all palette positions for the picker to jump to
function setAllPalPos(){
    for(let i=0;i<5;i++){
        let picker = document.getElementById("colorPick-"+i);
        let color = document.getElementById("color-"+i+"-"+WINDOW_SIZE);
        
        let x = parseInt(color.offsetLeft)
        let y = parseInt(color.offsetTop)
        let offx = (WINDOW_SIZE == "wide") ? -25 : 25;
        let offy = (WINDOW_SIZE == "wide") ? 60 : 13;
        
        // console.log(WINDOW_SIZE + "-"+i+": (" + x + ", " + y+")");
        color.ondblclick = gotoPalette(i,x+offx,y+offy);
    }
}

// add sprite list to the sprite list bar
function addSpriteList(){
    // for(let s=0; s<2; s++){
        // let cur_size = (s==0) ? "small" : "wide";
    let cur_size = "small";
    var spriteList = document.getElementById("sprite-list-"+cur_size);
    spriteList.innerHTML = "";
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

    if(SPR_INDEX < SPRITES.length-1)
        SPR_INDEX++;
    else
        SPR_INDEX = 0;
    setSelSheet(SPR_INDEX);
    showSprite();
}
// previous sprite in list
function prevSprite(){
    makeHistory();
    if(SPR_INDEX > 0)
        SPR_INDEX--;
    else
        SPR_INDEX = SPRITES.length-1;
    setSelSheet(SPR_INDEX);
    showSprite();
}

// if the sprite list is clicked, jump to the sprite - uses 7 list index
function onSprite(index){
    return function(){
        makeHistory();
        let lb = Math.max(0,Math.min(SPRITES.length-7,SPR_INDEX-3))
        // console.log("on sprite: " + (index+lb));
        SPR_INDEX = index+lb;
        setSelSheet(SPR_INDEX);
        showSprite();
    }
}

// if the sprite list is clicked, jump to the sprite - uses real index
function onSprite_sheet(d,real_index){
    return function(){
        makeHistory();
        SPR_INDEX = real_index;
        document.getElementsByClassName("sel-sht")[0].classList.remove("sel-sht");
        d.classList.add("sel-sht");
        showSprite();
    }
}

// set the selected sprite in the sheet
function setSelSheet(i){
    document.getElementsByClassName("sel-sht")[0].classList.remove("sel-sht");
    let spr_sheet = document.getElementsByClassName("ss-spr");
    spr_sheet[i].classList.add("sel-sht");

}

// jump to an index
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

// show the input text
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

    //update the sprite sheet
    updateSprSheet();
   

    //draw in the editor
    sprOnCanvas();
}

// draw in the canvas (specified with canvas and context)
function sprOnCanvas(canv=EDITOR, cont=ETX, ind=SPR_INDEX, cur_spr=null, TR_COL=null, PAL=null){
    if(TR_COL == null)
        TR_COL = TRANS_COLOR;
    if(PAL == null)
        PAL = PALETTE;

    //clear and draw transparency color
    cont.clearRect(0, 0, canv.width, canv.height);
    cont.fillStyle = TR_COL;
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
        var color = PAL[cur_spr[i]-1];
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

// add the sprites as images
function addSpriteSheet(){
    let ss_div = document.getElementById("ss_div");
    ss_div.innerHTML = "";
    
    //add all sprites
    for(let i=0;i<SPRITES.length;i++){
        let spr = document.createElement("img");

        //draw the sprite in the preview canvas
        sprOnCanvas(PREVIEW, PTX, i);
        spr.src = PREVIEW.toDataURL();
        spr.classList.add("ss-spr");
        if(i == SPR_INDEX)
            spr.classList.add("sel-sht");
        spr.onclick = onSprite_sheet(spr,i);

        //add to the div
        ss_div.appendChild(spr);
    }
    ss_div.style.backgroundColor = TRANS_COLOR;
}

// update a sprite's image in the sprite sheet
function updateSprSheet(){
    let spr_imgs = document.getElementById("ss_div").getElementsByTagName("img");
    sprOnCanvas(PREVIEW, PTX);
    spr_imgs[SPR_INDEX].src = PREVIEW.toDataURL();
}

// show the input at the current color palette location
// var PAL_WIDE = [{x:58,y:460},{x:142,y:460},{x:196,y:460},{x:248,y:460},{x:300,y:460}];
// var PAL_SMALL = [{x:575,y:135},{x:575,y:205},{x:575,y:255},{x:575,y:305},{x:575,y:355}];
function gotoPalette(i,x,y){
    return function(){
        // let pal_pos = (WINDOW_SIZE == "wide") ? PAL_WIDE : PAL_SMALL;
        console.log(x,y)
        let col_pick = document.getElementById("colorPick-"+WINDOW_SIZE);
        col_pick.style.left = x+"px";
        col_pick.style.top = y+"px";
        document.querySelector('#colorPick-'+WINDOW_SIZE).jscolor.fromString(i == 0 ? TRANS_COLOR : PALETTE[i-1]); //set color
        col_pick.style.display = "block";
        col_pick.focus();
    }
}

// set the color of the palette
function setPaletteColor(){
    let col_pick = document.getElementById("colorPick-"+WINDOW_SIZE);
    let col = col_pick.value;

    //update the palette and hide
    if(CUR_COLOR == 0){
        TRANS_COLOR = col;
        ss_div.style.backgroundColor = TRANS_COLOR; //reset the background color of sprite sheet
    }else
        PALETTE[CUR_COLOR-1] = col;
    col_pick.style.display = "none";

    //update the sprites
    sprOnCanvas();
    addSpriteList();
    addSpriteSheet();
    showSprite();

    //update all palettes
    for(let i=0;i<2;i++){
        let ch = document.getElementById("palette-"+(i==0?"small":"wide")).children;
        ch[CUR_COLOR].style.backgroundColor = col;
    }
    
}

// preview a new color on the current sprite
function previewNewCol(nc){
    if(CUR_COLOR == 0)
        sprOnCanvas(EDITOR,ETX,SPR_INDEX,null,nc,null);
    else{
        let pal = PALETTE.slice();
        pal[CUR_COLOR-1] = nc;
        sprOnCanvas(EDITOR,ETX,SPR_INDEX,null,null,pal);
    }

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


// show the debugs
let debug = document.getElementById("debug");
function update(){
    requestAnimationFrame(update);
    
    if (UNIV_PD != null){
        // debug.innerHTML = `M POS (${UNIV_PD.x}, ${UNIV_PD.y})`
        // debug.innerHTML += ` | M PRESS? ${mouseIsDown} `
        // debug.innerHTML += ` | TOUCH PT (${touchPt.x}, ${touchPt.y})`
        // debug.innerHTML += ` | `
    }

}
update();



///////////////     KEY PRESS SHORTCUTS     //////////////////

// key up (enter) to switch to sprite
document.getElementById("ind_in-"+WINDOW_SIZE).addEventListener("keyup", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        toSprite(this);
    }
});

// check for shortcut
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

    //iterate through sprites
    if (event.key == "ArrowLeft") {
        event.preventDefault();
        prevSprite();
    }
    else if (event.key == "ArrowRight") {
        event.preventDefault();
        nextSprite();
    }
});

//window resize
window.addEventListener('resize', function(event) {
    let pal1 = document.getElementById("color-"+CUR_COLOR+"-"+WINDOW_SIZE);
    let pick = document.getElementById("colorPick-"+WINDOW_SIZE);

    if(pal1 != null && pick != null){
        let ox = parseInt(pal1.offsetLeft);
        let oy = parseInt(pal1.offsetTop);

        if(WINDOW_SIZE == "small"){
            pick.style.left = (ox+25)+"px";
            pick.style.top = (oy+13)+"px";
        }else if(WINDOW_SIZE == "wide"){
            pick.style.left = (ox-25)+"px";
            pick.style.top = (oy+60)+"px";
        }
    }

    setAllPalPos();
}, true);