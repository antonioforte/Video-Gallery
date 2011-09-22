/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_deleteAllChildNodes(holder){

    while(holder.hasChildNodes()){
        holder.removeChild(holder.lastChild);
    }

}
/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_HideElementsOfClass(targetClass){
    var s = dom_getElementsOfClass(targetClass);
    for(var e = 0; e < s.length; e++){
            s[e].style.display = 'none';
        }
}
/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_showHideEl(el){
    if (el.style.display != 'block'){
        el.style.display = 'block';
    }else{
        el.style.display = 'none';
    }
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_containerGetElementsOfClass(container,targetClass){

    var matchingEls = [];
    var els = container.getElementsByTagName('*');
    for(var e = 0; e < els.length; e++){
    
        if (els[e].className == targetClass){
            matchingEls.push(els[e]);
        }  
        
    }
    return matchingEls;
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_getElementsOfClass(targetClass){

    var matchingEls = [];
    var els = document.getElementsByTagName('*');
    for(var e = 0; e < els.length; e++){
    
        if (els[e].className == targetClass){
            matchingEls.push(els[e]);
        }   
    }
    return matchingEls;
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_addPageHeader() {
    var headerDiv = document.createElement("div");
    headerDiv.setAttribute('id', 'pageHeader');
    // insert as body first node
    document.body.insertBefore(headerDiv, document.body.childNodes[0]);
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_addDocumentTitleDiv() {
    var docDiv = document.createElement("div");
    docDiv.setAttribute('id', 'docDiv');
    
    var docTitle = document.title;
    var docText = document.createTextNode(docTitle);
    docDiv.appendChild(docText);
    
    document.body.appendChild(docDiv);
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_onDomReady(function_name){

    var hasRun = "no";

    /* for Mozilla/Opera9 */
    if (document.addEventListener) {
      document.addEventListener("DOMContentLoaded", function_name, false);
      hasRun = "yes";
    }

    /* for other browsers */
    if (hasRun == "no"){
        window.onload = function_name;
    }
    
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_addEventListener(target, eventType, eventFunction){  
    if(target.addEventListener){
        target.addEventListener(eventType,eventFunction,false);
    }else if(target.attachEvent){
        target.attachEvent("on"+eventType,eventFunction);
    }else{
        alert("Could not attach event");
    }  
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

function dom_getEventObj(event){  

    var theObj = 'not';

    if(event.target){var theObj = event.target;}
    if(event.srcElement){var theObj = event.srcElement;} 
    
    return theObj;
}

/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/

var print = new Object();

print.init = function(){
    var hasprintdiv = document.getElementById('print');
    var text = '';
    
    for (var i=0; i<arguments.length; i++) {
        text += ' , '+arguments[i];
    }

    if (hasprintdiv){
        var p = document.createElement('p');
        var text = document.createTextNode(text) ;
        p.appendChild(text); 
        hasprintdiv.appendChild(p);
    }
    
    if (!hasprintdiv){
        var div = document.createElement('div');
        div.setAttribute('id','print'); 
        document.body.appendChild(div);

        var hasprintdiv = document.getElementById('print');
        hasprintdiv.style.background = '#333';
        hasprintdiv.style.position = 'absolute';
        hasprintdiv.style.bottom = '10px';
        hasprintdiv.style.right = '10px';
        hasprintdiv.style.height = '150px';
        hasprintdiv.style.width = '400px';
        hasprintdiv.style.overflow = 'scroll';
        
        var p = document.createElement('p');
        var text = document.createTextNode(text) ;
        p.appendChild(text); 
        hasprintdiv.appendChild(p);
    }

}
/*xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx*/




