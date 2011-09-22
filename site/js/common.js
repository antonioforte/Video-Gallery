



var LibCommon = new Object();
LibCommon.init = function(){
    var profiles2sort = ['Movies','TV'];
    var mode = document.body.getAttribute('data-mode');
    var profile = document.body.getAttribute('data-profile');
    
    if (mode == 'front') {
        if (profiles2sort.indexOf(profile) != -1){
            navletters.init('frontWrapper',16);
        }
    }
}

//Let the games begin
dom_onDomReady(LibCommon.init);
//end
