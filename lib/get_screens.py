import os
from PySide import QtCore





class getScreens(QtCore.QObject):

    def set_values(self,frame):
        self.frame = frame


    @QtCore.Slot(str)
    def gomouseover(self,url):
        self.calling_img = self.get_calling_img(url)
        self.screenslist = self.get_movie_screens(url) 

        screensobj = QtCore.QObject()
        screensobj.setObjectName("screens")

        self.intervalobj = QtCore.QObject()
        self.intervalobj.setObjectName("intervalobj")

        self.frame.addToJavaScriptWindowObject("intervalobj",self.intervalobj)
        self.frame.addToJavaScriptWindowObject("screens",screensobj)

        if len(self.screenslist) != 0 and self.calling_img:
            print('found',len(self.screenslist),'screens')
            screensobj.setProperty("screenlist",self.screenslist)
            self.calling_img.evaluateJavaScript('''
                var screens = screens.screenlist;
                var cur_screen = 0;
                var img_el = this;

                img_el.setAttribute('data-defaultsrc',img_el.getAttribute('src'));
                intervalobj = window.setInterval("cycle_screen()",1000);
    
                function cycle_screen(){
                    if (cur_screen == screens.length){
                        cur_screen = 0;
                    }
                    img_el.setAttribute('src','file:///'+screens[cur_screen]);
                    cur_screen++;
                }''')
    
    
    @QtCore.Slot(str)
    def gomouseout(self,url):
        # sometimes mouseout is called before any mouseover
        if self.calling_img:
            self.calling_img.evaluateJavaScript('''
                clearInterval(intervalobj);
                var img_el = this;
                img_el.setAttribute('src',img_el.getAttribute('data-defaultsrc'));''')
        
        
        
    def get_movie_screens(self,url):
        dirname, filename = os.path.split(url)
        filebasename = os.path.splitext(filename)[0]
        screensdir = os.path.join(dirname,'screens')
        screenslist = []
        
        if os.path.exists(screensdir):
            try:
                screens = os.listdir(screensdir)
                for screen in screens:
                    screenurl = os.path.join(screensdir,screen)
                    screenfilebasename,ext = os.path.splitext(screen)
                    # excess chars used for numbering

                    nchars = len(screenfilebasename.replace(filebasename,''))
                    screenlabel = screenfilebasename[:-nchars]

                    if screenlabel == filebasename:
                        screenslist.append(screenurl)
            except Exception as e:
                print ("Error getImgOvers.get_movie_screens : ",e)
        return screenslist
    
    
    
    def get_calling_img(self,url):
        calling_img = False
        imgs = self.frame.findAllElements("img.fileScreen").toList()
        for img in imgs:
            if img.attribute('data-url') == url:
                calling_img = img
        return calling_img
        
        
        
        
        
        
        
        
        
        
        
        
        
        