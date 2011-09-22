
var navletters = new Object();
navletters.wrapper = '';
navletters.all = [];
navletters.letters = [];

navletters.init = function(id,num){
    var wrapper = document.getElementById(id);
    var childs = wrapper.childNodes;
    navletters.wrapper = wrapper;

    for(var e = 0; e < childs.length; e++){
        var label = childs[e].getAttribute('data-movie_label');
        var firstletter = label.substr(0,1);
        navletters.all.push(childs[e]);
        
        if (navletters.letters.indexOf(firstletter) == -1){
            navletters.letters.push(firstletter);
        }
    }
    
    if (navletters.all.length > num){
        wrapper.style.marginTop = '85px';
        navletters.createButtons();
    }
}


navletters.createButtons = function(){
    var buttonsdiv = document.createElement('div');
    buttonsdiv.id = 'buttonsdiv';
    
    var buttonall = document.createElement('button');
    buttonall.textContent = 'all';
    buttonall.addEventListener('mouseup',navletters.sort,false);
    buttonsdiv.appendChild(buttonall);
    
    for(var e = 0; e < navletters.letters.length; e++){
        var button = document.createElement('button');
        button.textContent = navletters.letters[e];
        button.addEventListener('mouseup',navletters.sort,false);
        buttonsdiv.appendChild(button);
    }
    document.body.insertBefore(buttonsdiv,navletters.wrapper);
}


navletters.sort = function(evt){
    dom_deleteAllChildNodes(navletters.wrapper);
    var query = event.srcElement.textContent;

    if (query != 'all'){
        for(var e = 0; e < navletters.all.length; e++){
            var label = navletters.all[e].getAttribute('data-movie_label');
            var firstletter = label.substr(0,1);
            if (firstletter == query){
                navletters.wrapper.appendChild(navletters.all[e]);
            }
        }
    }else{
        for(var e = 0; e < navletters.all.length; e++){
            navletters.wrapper.appendChild(navletters.all[e]);
        }
    }  
}


/* end */