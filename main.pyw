#!/usr/bin/env python
from xml.etree import ElementTree as ET
import threading
import sqlite3
import subprocess
import sys
import os
import time

from PySide import QtCore
from PySide import QtGui
from PySide import QtWebKit
from PySide import QtNetwork
from PySide.phonon import Phonon

import lib.common
import lib.templates
import lib.build_db
import lib.query_db
import lib.launch_video
import lib.video_player
import lib.get_screens

# pyside-uic videoplayerframe.ui -o gui.py
# pyuic4 videoplayerframe.ui -o gui.py

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.lib = lib.common.common() 
        self.templates = lib.templates.templates()
        
        self.curdir = self.getMainDir()
        self.configxml = self.lib.getXml(os.path.join(self.curdir, 'config.xml'))
        self.dbpath = os.path.join(self.curdir, 'res', 'data.db')
        
        self.resize(1200, 700)
        self.setWindowTitle('New Video Gallery')
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.curdir, 'res','graphics', 'app_icon.png')))
        self.center()

        self.buildDB = lib.build_db.buildDb()
        self.buildDB.postBuildDbSig.connect(self.buildDB_update_status)
        self.buildDB.startBuildDbSig.connect(self.buildDB_start)
        self.buildDB.endBuildDbSig.connect(self.buildDB_end)

        self.queryDB = lib.query_db.queryDb()
        self.queryDB.set_values(self.curdir, self.configxml, self.dbpath)
        self.queryDB.postQueryDbSig.connect(self.queryDB_post_query)
        self.queryDB.startQueryDbSig.connect(self.queryDB_start)
        self.queryDB.endQueryDbSig.connect(self.queryDB_end)
      
        self.launch_video = lib.launch_video.launchVideo()
        self.launch_video.startHereSignal.connect(self.play_here)
        
        self.get_screens = lib.get_screens.getScreens()
        
        # create webkit and load start page
        self.theinit('not')

         
    def play_here(self, video_url):
        #remove goback div because it will be created
        # based on the tag body attributes
        goback = self.mainframe.findFirstElement('div#goback')
        goback.removeFromDocument()
        self.backhtml = self.mainframe.toHtml()
        
        self.web.close()

        vid = lib.video_player.thePlayer(self, video_url)
        back = self.findChild(QtGui.QPushButton, 'back')
        back.clicked.connect(self.goback)


    def goback(self):
        childs1 = self.findChild(Phonon.VideoPlayer, 'player')
        childs2 = self.findChild(QtGui.QFrame, 'framePlayControl')
        childs1.deleteLater()
        childs2.deleteLater()
        # create webkit and load the last html page loaded
        self.theinit(self.backhtml)
        

    def theinit(self, html):
        self.web = QtWebKit.QWebView(self)
        self.web.loadFinished.connect(self.web_load_end)

        self.web.setRenderHints(QtGui.QPainter.HighQualityAntialiasing | 
                                QtGui.QPainter.SmoothPixmapTransform | 
                                QtGui.QPainter.TextAntialiasing)

        self.websettings = self.web.settings()
        self.websettings.setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, 7)
        #self.websettings.setAttribute(QtWebKit.QWebSettings.ZoomTextOnly,9)

        self.page = self.web.page()
        self.mainframe = self.page.mainFrame()
        self.mainframe.javaScriptWindowObjectCleared.connect(self.js_cleared)

        startpage = os.path.join(self.curdir, 'site', 'index.html')
        if html == 'not':
            self.web.load(QtCore.QUrl(startpage))
        else:
            self.web.setHtml(html)
        
        self.setCentralWidget(self.web)
        self.web.show()


    def buildDB_update_status(self, html):
        print('buildDB_update_status')
        results = self.mainframe.findFirstElement("div#results")
        results.setStyleProperty('display','block')
        results.setPlainText('')
        results.appendInside(html)
         
         
    def buildDB_start(self, html):
        print('buildDB_start')
        results = self.mainframe.findFirstElement("div#results")
        results.setStyleProperty('display','block')
        results.setPlainText('Starting scan...')
        
    def buildDB_end(self, html):
        print('buildDB_end')
        results = self.mainframe.findFirstElement("div#results")
        results.setStyleProperty('display','block')
        span = ET.Element('span')
        span.text = 'Ending scan...'
        results.appendInside(ET.tostring(span))



    def queryDB_post_query(self, html):
        print('queryDB_post_query')
        self.web.setHtml(html)
        
    def queryDB_start(self, html):
        print('queryDB_start', html)
        self.web.setHtml(html)
        
    def queryDB_end(self, html):
        print('queryDB_end')



    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
        

    def keyPressEvent(self, event):
        '''This method does not need to be instanciated
        because self is a MainWindow.
        MainWindow looks for a keyPressEvent method'''
        if event.key() == QtCore.Qt.Key_X:
            self.showFullScreen()
        if event.key() == QtCore.Qt.Key_C:
            self.showNormal()
        if event.key() == QtCore.Qt.Key_U:
            self.web.setZoomFactor(1.5)
        if event.key() == QtCore.Qt.Key_I:
            self.web.setZoomFactor(1)
        if event.key() == QtCore.Qt.Key_O:
            self.web.setZoomFactor(0.8)
        if event.key() == QtCore.Qt.Key_S:
            self.theinit('not')


    def web_load_end(self):
        print ('web_load_End')
        title = self.web.title()
        
        self.create_goback()
        self.apply_events_front()
        self.apply_events_afterfront()
        self.get_screens.set_values(self.mainframe)
        
        if title == 'Hall':
            self.get_starting_html()
        if title == 'Edit':
            self.buildDB.set_values(self.curdir, self.configxml, self.dbpath)
            self.mainframe.addToJavaScriptWindowObject("build_db", self.buildDB)
        
        
            
    def create_goback(self):
        '''
        Create goback menu according the body tag attributtes.
        If the attributes indicate that we are in an afterfront page profile, 
        a back link, which calls the front level of the profile is created.
        If we are in front level just create link to home.
        '''
        body = self.mainframe.findFirstElement('body')
        mode = body.hasAttribute('data-mode')

        if mode:
            goback = ET.Element('div', {'id':'goback'})
            leftdiv = ET.SubElement(goback, 'div', {'class':'left'})
            homelink = ET.SubElement(leftdiv, 'a')
            homelink.attrib['href'] = 'file://' + os.path.join(self.curdir, 'site', 'index.html')
            homelink.text = 'Hall'
            
            if body.attribute('data-mode') != 'front':
                back = ET.SubElement(leftdiv, 'span', {'id':'backspan'})
                back.attrib['data-mode'] = body.attribute('data-mode')
                back.attrib['data-profile'] = body.attribute('data-profile')
                back.attrib['data-label'] = body.attribute('data-label')
                back.attrib['data-url'] = body.attribute('data-url')
                back.text = body.attribute('data-label')

            body.appendInside(ET.tostring(goback))
            backspan = self.mainframe.findFirstElement('span#backspan')
            backspan.evaluateJavaScript('''
                this.addEventListener('mouseup', function(e) { 
                    var profile = this.getAttribute('data-profile');
                    var label = this.getAttribute('data-label');
                    var url = this.getAttribute('data-url');
                
                    query_db.go('front',profile,label,url,'none','none');
                },false);
                ''')



    def apply_events_afterfront(self):
        body = self.mainframe.findFirstElement('body')
        mode = body.hasAttribute('data-mode')
        if mode:
            if body.attribute('data-mode') != 'front':
                
                # show hide files
                for span in body.findAll('span.spanShowEpisodes').toList():
                    span.evaluateJavaScript('''
                        this.addEventListener('mouseup', function(e) { 
                            var wrapper = this.parentNode.parentNode;
                            var table = wrapper.getElementsByTagName('table')[0];
                            var table_state = table.style.display;
    
                            if (table_state == 'table'){table.style.display = 'none';}
                            else{table.style.display = 'table';}
                        },false);''')


                # show hide img storyboard
                for span_ in body.findAll('span.spanShowStoryboard').toList():
                    span_.evaluateJavaScript('''
                        this.addEventListener('mouseup', function(e) { 
                            var wrapper = this.parentNode.parentNode;
                            var img = wrapper.getElementsByTagName('img')[0];
                            var img_state = img.style.display;
    
                            if (img_state == 'inline'){img.style.display = 'none';}
                            else{img.style.display = 'inline';}
                        },false);''')


                # launch videos
                for span2 in body.findAll('span.video_launcher').toList():
                    span2.evaluateJavaScript('''
                        this.addEventListener('mouseup', 
                            function(e) { 
                                var video_url = this.getAttribute('data-video_url');
                                var app = this.getAttribute('data-app');

                                launch_video.go(app,video_url);
                            },false);''')
                    
                    
                    
                    
                    
                    
                # get screens apply events
                for file_screen in body.findAll('img.fileScreen').toList():
                    file_screen.evaluateJavaScript('''
                        this.addEventListener('mouseover', 
                            function(e) { 
                                var url = this.getAttribute('data-url');
                                get_screens.gomouseover(url);
                            }
                        ,false);
                        
                        this.addEventListener("mouseout", 
                            function(evt) { 
                                var url = this.getAttribute('data-url');
                                get_screens.gomouseout(url);
                            }, 
                        false);''')
                
                
        

    def apply_events_front(self):
        body = self.mainframe.findFirstElement('body')
        mode = body.attribute('data-mode')
        locprofile = body.attribute('data-profile')
        loclabel = body.attribute('data-label')
        locurl = body.attribute('data-url')

        if mode == 'front':
            for movie in body.findAll('div.movieWrapper').toList():
                movie.evaluateJavaScript('''
                    this.addEventListener('mouseup', function(e) { 
                        var profile = document.body.getAttribute('data-profile');
                        var label = document.body.getAttribute('data-label');
                        var url = document.body.getAttribute('data-url');
                        var movie = this.getAttribute('data-movie_label');
                    
                        query_db.go('afterfront',profile,label,url,movie,'none');
                    },false);
                    ''')



    def js_cleared(self):
        print ('Javascript objects cleared')
        self.mainframe.addToJavaScriptWindowObject("query_db", self.queryDB)
        self.mainframe.addToJavaScriptWindowObject("launch_video", self.launch_video)
        self.mainframe.addToJavaScriptWindowObject("get_screens", self.get_screens)


    def get_starting_html(self):
        indexwrapper = self.mainframe.findFirstElement('div#indexWrapper')
        if indexwrapper:
            folders = self.get_starting_html_string()
            indexwrapper.appendInside(folders)
            
            for folder in indexwrapper.findAll('div.indexFolderWrapper').toList():
                folder.evaluateJavaScript('''
                    this.addEventListener('mouseup', function(e) { 
                        var profile = this.getAttribute('data-profile');
                        var label = this.getAttribute('data-label');
                        var url = this.getAttribute('data-url');
                    
                        query_db.go('front',profile,label,url,'none','none');
                    },false);
                    ''')
                
   
    def get_starting_html_string(self):
        html = ''
        folders = self.configxml.find('video_folders')
        for folder in folders.getiterator('folder'):
            div = ET.Element('div', {'class':'indexFolderWrapper'})
            div.text = folder.attrib['label']
            div.attrib['data-profile'] = folder.attrib['profile']
            div.attrib['data-label'] = folder.attrib['label']
            div.attrib['data-url'] = folder.text
            
            html += ET.tostring(div, 'utf-8')
        return html
        

        
    def getMainDir(self):
        '''Get script or exe directory.'''
        if hasattr(sys, 'frozen'): #py2exe, cx_freeze
            app_path = os.path.dirname(sys.executable)
            print ('Executing exe', app_path)
        elif __file__: #source file          
            app_path = os.path.abspath(os.path.dirname(__file__))
            print ('Executing source file', app_path)
        return app_path 
       
       

       
       
       
if __name__ == "__main__":
    '''Get script or exe directory.'''
    app_path = ''
    if hasattr(sys, 'frozen'): #py2exe, cx_freeze
        app_path = os.path.dirname(sys.executable)
    elif __file__: #source file
        app_path = os.path.dirname(__file__)

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("New video gallery")
    
    splash_pix = QtGui.QPixmap(os.path.join(app_path, 'res', 'graphics', 'splash.png'))
    splash = QtGui.QSplashScreen(splash_pix)
    splash.setMask(splash_pix.mask())
    splash.show()

    time.sleep(3)

    main = MainWindow()
    splash.finish(main)
    main.show()

    sys.exit(app.exec_())




        




