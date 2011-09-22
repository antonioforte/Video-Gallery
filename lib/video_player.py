import time
import os
import parse_subs
from PySide import QtCore
from PySide import QtGui
from PySide.phonon import Phonon


class thePlayerEventFilter(QtCore.QObject):
    mouseHasMoved = QtCore.Signal(int,int)
    
    def __init__(self,parent):
        QtCore.QObject.__init__(self,parent)
        
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.MouseMove:
            self.mouseHasMoved.emit(event.x(),event.y())
            return True
        else:
            return False





class thePlayer(Phonon.VideoPlayer):
    '''
    This creates a VideoPlayer widget and sets it
    as the main window CentralWidget.
    Then the control widget is appended.
    When the mouse is in the lower part of the 
    VideoPlayer widget, the control widget changes its
    geometry to show itself. 
    '''
    def __init__(self, parent,video_url):
        Phonon.VideoPlayer.__init__(self,parent)
        self.parent = parent

        self.player = Phonon.VideoPlayer(self.parent)
        self.player.setObjectName('player')
        self.parent.setCentralWidget(self.player)
        
        self.playerWidget = self.player.videoWidget()
        self.playerWidget.setCursor(QtCore.Qt.BlankCursor)
        self.player.load(Phonon.MediaSource(video_url))

        self.player.show()
        self.player.setVolume(0.5)
        self.player.play()

        self.control = playControl(self.parent,self.player)

        # Parse mouse events on the player widget
        self.playerWidget.setMouseTracking(True)
        self.filter = thePlayerEventFilter(self)
        self.filter.mouseHasMoved.connect(self.show_control)
        self.playerWidget.installEventFilter(self.filter)

        self.playbtn = self.control.frame.findChild(QtGui.QPushButton,'play')
        self.playbtn.clicked.connect(self.play_video)
        
        self.fullscreen = self.control.frame.findChild(QtGui.QPushButton,'fullscreen')
        self.fullscreen.clicked.connect(self.gofullscreen)
        
        self.timelabel = self.control.frame.findChild(QtGui.QLabel,'labelTime')
        self.player.mediaObject().tick.connect(self.show_time)

        self.enablesubs = self.control.frame.findChild(QtGui.QCheckBox,'enablesubs')
        self.enablesubs.stateChanged.connect(self.hide_show_subs)

        self.hassubs,self.subsentries = self.get_subtitles(video_url)
        if self.hassubs == 'yes' and self.enablesubs.isChecked():
            self.create_subs_label()
             


    def get_subtitles(self,video_url):
        url, ext = os.path.splitext(video_url)
        subfile = os.path.join(url+'.srt')
        hassubs = 'no'
        entries = []
        
        if os.path.exists(subfile):
            entries = parse_subs.getSubtitles(subfile)
            hassubs = 'yes'
        return hassubs,entries
        
        
        
    def create_subs_label(self):
        winwidth = self.parent.width()
        subspos = self.parent.height() - 50

        self.labelsubs = QtGui.QLabel(self.player)
        self.labelsubs.setGeometry(0,subspos,winwidth,50)
        self.labelsubs.setText('subtitles')
        self.labelsubs.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter)
        self.labelsubs.setStyleSheet("QLabel { background-color:#0a0a0a; color : white; }")
        self.labelsubs.setObjectName("labelsubs")
        self.labelsubs.show()

        
                
    def position_subslabel(self):
        winheight = self.parent.height()
        winwidth = self.parent.width()
        labelpos = self.labelsubs.y()
        subspos = winheight - 50

        if self.labelsubs.width() != winwidth or labelpos != subspos:
            self.labelsubs.setGeometry(0,subspos,winwidth,50)
            self.labelsubs.updateGeometry()
            self.labelsubs.update()
        
        
        
    def show_time(self,cur_time):
        cur_total = self.player.mediaObject().totalTime()
        curtime = time.strftime("%H:%M:%S", time.gmtime(cur_time/1000))
        curtotal = time.strftime("%H:%M:%S", time.gmtime(cur_total/1000))
        self.timelabel.setText(curtime+' / '+curtotal)
        
        if self.player.findChild(QtGui.QLabel,'labelsubs'):
            self.insert_subtitle(cur_time)
        
        
        
    def insert_subtitle(self,cur_time): 
        self.position_subslabel()
        for item in self.subsentries.entries:
            start = item.start
            end = item.end

            if cur_time >= start:
                text = ''
                for line in item.lines:
                    text += line
                self.labelsubs.setText(text)
                if cur_time >= end:
                    self.labelsubs.clear()

                

    def hide_show_subs(self,state):
        '''Signal reacting to checkbox enable subs'''
        if state == 2:
            self.create_subs_label()
        if state == 0:
            if self.player.findChild(QtGui.QLabel,'labelsubs'):
                self.labelsubs.deleteLater()
            
        

    def gofullscreen(self):
        if self.parent.isFullScreen():
            self.parent.showNormal()
        else:
            self.parent.showFullScreen()
            


    def play_video(self):
        if self.player.isPlaying():
            self.player.pause()
            self.playbtn.setText('play')
        else:
            self.player.play()
            self.playbtn.setText('pause')



    def show_control(self,x,y):
        '''If mouse is on the lower 100px of
        video player widget, show the menu,
        if not hide it.
        '''
        winheight = self.parent.height()
        controlheight = 100
        statbarheight = 0
        yline = winheight - controlheight
        
        if y >= yline and y <= winheight:
            self.show_menu(yline - statbarheight)
        else:
            self.hide_menu()
        


    def show_menu(self,yline):
        self.control.frame.setGeometry(0,yline,self.parent.width(),100)
        self.control.frame.setAutoFillBackground(True)
        self.control.frame.updateGeometry()
        self.control.frame.update()



    def hide_menu(self):
        self.control.frame.setGeometry(0,0,0,0)
        self.control.frame.updateGeometry()
        self.control.frame.update()



class playControl(QtGui.QWidget):
    def __init__(self, parent,vid):
        QtGui.QWidget.__init__(self, parent)
        # row,  column,  rowSpan, columnSpan
        
        self.frame = QtGui.QFrame(parent)
        self.frame.setObjectName('framePlayControl')
        self.gridLayout = QtGui.QGridLayout()

        fixed_size_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        
        self.seekSlider = Phonon.SeekSlider(self.frame)
        self.seekSlider.setMediaObject(vid.mediaObject())
        self.gridLayout.addWidget(self.seekSlider, 0, 0, 1, 5)

        self.volumeSlider = Phonon.VolumeSlider(self.frame)
        self.volumeSlider.setAudioOutput(vid.audioOutput())
        self.gridLayout.addWidget(self.volumeSlider, 1, 0, 1, 5)

        #horizontalLayout 1
        self.horizontalLayout_1 = QtGui.QHBoxLayout()
        self.previous = QtGui.QPushButton(self.frame)
        self.previous.setText('previous')
        self.previous.setSizePolicy(fixed_size_policy)
        self.previous.setObjectName('previous')
        self.horizontalLayout_1.addWidget(self.previous)
        
        self.play = QtGui.QPushButton(self.frame)
        self.play.setText('pause')
        self.play.setSizePolicy(fixed_size_policy)
        self.play.setObjectName('play')
        self.horizontalLayout_1.addWidget(self.play)
        
        self.next = QtGui.QPushButton(self.frame)
        self.next.setText('next')
        self.next.setSizePolicy(fixed_size_policy)
        self.next.setObjectName('next')
        self.horizontalLayout_1.addWidget(self.next)
        
        self.back = QtGui.QPushButton(self.frame)
        self.back.setText('back')
        self.back.setSizePolicy(fixed_size_policy)
        self.back.setObjectName('back')
        self.horizontalLayout_1.addWidget(self.back)
        
        self.gridLayout.addLayout(self.horizontalLayout_1, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(84, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        
        #horizontalLayout 2
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.playlistBTN = QtGui.QPushButton(self.frame)
        self.playlistBTN.setObjectName("playlistBTN")
        self.playlistBTN.setText('playlist')
        self.playlistBTN.setSizePolicy(fixed_size_policy)
        self.horizontalLayout_2.addWidget(self.playlistBTN)
        
        self.enhanceBTN = QtGui.QPushButton(self.frame)
        self.enhanceBTN.setObjectName("enhanceBTN")
        self.enhanceBTN.setText('enhance')
        self.enhanceBTN.setSizePolicy(fixed_size_policy)
        self.horizontalLayout_2.addWidget(self.enhanceBTN)
        
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 2, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(138, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 3, 1, 1)
        
        #horizontalLayout 3
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.subsBTN = QtGui.QPushButton(self.frame)
        self.subsBTN.setObjectName("subsBTN")
        self.subsBTN.setSizePolicy(fixed_size_policy)
        self.subsBTN.setText('subs')
        self.horizontalLayout_3.addWidget(self.subsBTN)
        
        self.fullscreen = QtGui.QPushButton(self.frame)
        self.fullscreen.setText('fullscreen')
        self.fullscreen.setSizePolicy(fixed_size_policy)
        self.fullscreen.setObjectName('fullscreen')
        self.horizontalLayout_3.addWidget(self.fullscreen)

        self.checkBox = QtGui.QCheckBox(self.frame)
        self.checkBox.setObjectName('enablesubs')
        self.horizontalLayout_3.addWidget(self.checkBox)
        
        self.labelTime = QtGui.QLabel(self.frame)
        self.labelTime.setText('00:00:00 / 00:00:00')
        self.labelTime.setSizePolicy(fixed_size_policy)
        self.labelTime.setObjectName("labelTime")
        self.horizontalLayout_3.addWidget(self.labelTime)

        self.gridLayout.addLayout(self.horizontalLayout_3, 2, 4, 1, 1)
        self.frame.setLayout(self.gridLayout)

        self.frame.setGeometry(0,0,0,0)
        self.setUpdatesEnabled(True)
        self.frame.show()
        

        
        
        
        