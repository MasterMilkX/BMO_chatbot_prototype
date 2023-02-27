// MAIN CODE THAT CONNECTS ALL OF BMO TOGETHER


// main initialization function
function MAIN_INIT(){
    CODE_INIT();
    SPRITE_INIT();
}



// - editor functions - //

//change which screen the editor window shows
function CHANGE_EDITOR(modeTab){
    let mode = modeTab.innerHTML.toLowerCase();

    //hide all the other windows and unselect tabs
    let all_windows = document.getElementsByClassName("editor-window");
    for (let i = 0; i < all_windows.length; i++){
        all_windows[i].style.display = "none";
    }
    let all_tabs = document.getElementsByClassName("tool-item-right");
    for (let i = 0; i < all_tabs.length; i++){
        all_tabs[i].classList.remove("tool-select");
    }


    //show the selected window and tab
    let selected_window = document.getElementById(mode + "-editor");
    selected_window.style.display = "flex";
    modeTab.classList.add("tool-select");

    //sprite mods
    if(mode == "sprite"){
        setAllPalPos();
    }

}


// show/hide bmo and resize the editor window
function TOGGLE_BMO(){
    let chat_window = document.getElementById("right-half");
    let editor_window = document.getElementById("editor");
    
    //show the window \ short layout
    if (chat_window.style.display == "none"){

        chat_window.style.display = "block";
        showIcon("awake");
        editor_window.style.width = "620px";


        
        document.getElementById("spr-editor-small").style.display = "block";
        document.getElementById("spr-editor-wide").style.display = "none";
        WINDOW_SIZE = "small";
        document.getElementById("spritesheet").style.display = "none";


    } 
    //hide the window \ wide layout
    else {


        chat_window.style.display = "none";
        showIcon("off");
        editor_window.style.width = "900px";


        //resize the sprite window if visible
        document.getElementById("spr-editor-small").style.display = "none";
        document.getElementById("spr-editor-wide").style.display = "block";
        WINDOW_SIZE = "wide";
        document.getElementById("spritesheet").style.display = "block";


    }

    ///////    CODE EDITOR    /////////

    ace_editor.resize()  //resize the code editor


    ///////    SPRITE EDITOR    /////////

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