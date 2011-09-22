import subprocess
from PySide import QtCore


class launchVideo(QtCore.QObject):
    startHereSignal = QtCore.Signal(str)

    @QtCore.Slot(str,str)
    def go(self,app,video_url):
        if app != 'here':
            self.open_external_app(video_url,app)
        if app == 'here':
            self.startHereSignal.emit(video_url)


    def open_external_app(self,video_url,app):      
        try:
            cmd = [app]
            cmd.append(video_url)
            retval = subprocess.Popen(cmd)
        except Exception as e:
            print ("Error could not execute launchVideo. ",e.args)

