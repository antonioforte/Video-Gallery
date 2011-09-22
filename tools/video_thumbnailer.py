from xml.etree import ElementTree as ET
import Image
import ImageOps
import subprocess
import datetime
import sys
import os
import glob
import time
from hachoir_parser import createParser
from hachoir_metadata import extractMetadata

'''Find video files in dirs.
For each video.
    Divide video total time by number of shots.
    Create screens dir where video file is found.
    Create screens jpgs in screens dir for each video. 
    Resize screens.
    
Todo : 
    When a video file is renamed , 
    new screens have to created.
    The old screens will need to be erased.
    This should happen on a normal run.
'''


class Main:
    def __init__(self):
        print('----------------------------------')
        print('Video Thumbnailer start')
        
        self.configxml = self.get_config_xml()
        self.delete_existing_screens = self.configxml.find('delete_existing_screens').text
        self.nshots = int(self.configxml.find('nshots').text)
        self.screendims = self.configxml.find('screendims').text.split(',')
        self.totalvideos = 0
        self.fileswithzerotime = []
        begin_time = time.time()

        # go !!!
        profiles = self.get_dirs()
        exts = self.configxml.find('video_exts').text.split(',')
        for profile in profiles:
            self.run(profile,exts)
    
        print('-------------------------------------')
        for item in self.fileswithzerotime:
            print('0 duration',item)
        total_time = time.strftime("%H:%M:%S", 
                           time.gmtime(time.time() - begin_time))
        print('time taken',total_time)
        print('total videos',self.totalvideos)
        print('the end')
        print('-------------------------------------')





    def run(self,profile,exts):
        allfiles = self.get_all_video_files(profile, exts)

        # delete_existing_screens 
        if self.delete_existing_screens == 'yes':
            for uniqueurl in self.get_unique_urls(allfiles):
                self.delete_screens(os.path.join(uniqueurl,'screens'))

        # make screens 
        for fullurl in allfiles:
            hasscreens = self.check_if_has_screens(fullurl)

            if hasscreens != 'yes':
                dirname, filename = os.path.split(fullurl)
                filebasename,ext = os.path.splitext(filename)
                screensdir = os.path.join(dirname,'screens')
                
                # get metadata
                meta = self.get_metadata(fullurl)
                duration = self.get_start_time(meta)

                # if metadata is good
                if duration.seconds != 0:
                    self.make_screen_dir(screensdir)
                    snapintervalsecs = duration.seconds / self.nshots
                    startime = 0
                    
                    # ffmpeg will be started self.nshots times 
                    # for each video file.
                    # Each time ffmpeg is started the ss flag is incremented.
                    # This ss flag is the division between self.nshots
                    # and the length of the file  
                    for i in range(self.nshots):
                        cmd = self.get_ffmpeg_cmd(fullurl,screensdir,filebasename,startime,i)
                        self.run_cmd(cmd)
                        
                        # increment start time for the ss flag of ffmpeg
                        startime += snapintervalsecs
                        
                    # resize screens just created
                    self.resize_screens(screensdir,filebasename)
                        
                if duration.seconds == 0:
                    self.fileswithzerotime.append(fullurl)
                self.totalvideos += 1

    
                
    def get_ffmpeg_cmd(self,fullurl,screensdir,filebasename,startime,i):
        #ffmpeg -i input.dv -r 25 -ss 00:00:10 -t 00:00:05 -f image2 images%05d.png

        cmd = ['ffmpeg']

        cmd.append('-ss')
        cmd.append(str(startime))

        cmd.append('-i')
        cmd.append(fullurl)

        cmd.append('-vframes')
        cmd.append('1')

        cmd.append('-f')
        cmd.append('image2')

        picspath = os.path.join(screensdir,filebasename+' - '+str(i)+'.jpg')
        cmd.append(picspath)

        return cmd
    
    
    
    def resize_screens(self,screensdir,filebasename):
        '''Find screens of video file and resize them.'''
        if os.path.exists(screensdir):
            try:
                screens = os.listdir(screensdir)
                for screen in screens:
                    screenpath = os.path.join(screensdir,screen)
                    screenfilebasename = os.path.splitext(screen)[0]
                    nchars = len(screenfilebasename.replace(filebasename,''))
                    screenlabel = screenfilebasename[:-nchars]
                    
                    if screenlabel == filebasename:
                        im = Image.open(screenpath) 
                        imsizeor = [im.size[0],im.size[1]]
                        dims = [int(self.screendims[0]),int(self.screendims[1])]

                        method = Image.ANTIALIAS
                        bleed = 0
                        centering = (0.5,0.5)
                        e = ImageOps.fit(im,dims,method,bleed,centering)
                        e.save(screenpath)
                        print('resizing screen : ',screenpath)
            except Exception as e:
                print ("Error resize_screens: ",e)
                

    
    def check_if_has_screens(self,fullurl):
        dirname, filename = os.path.split(fullurl)
        filebasename = os.path.splitext(filename)[0]
        screensdir = os.path.join(dirname,'screens')
        has_screens = 'no'
        
        if os.path.exists(screensdir):
            try:
                screens = os.listdir(screensdir)
                for screen in screens:
                    screenfilebasename = os.path.splitext(screen)[0]
                    nchars = len(screenfilebasename.replace(filebasename,''))
                    screenlabel = screenfilebasename[:-nchars]
                    
                    if screenlabel == filebasename:
                        has_screens = 'yes'
            except Exception as e:
                print ("Error check_if_has_screens: ",e)
        return has_screens
        
    
    
    def get_all_video_files(self, profile, exts):
        allfiles = []
        try:
            for root, dirs, files in os.walk(unicode(profile)):
                for fn in files:
                    fullurl = os.path.join(root, fn)
                    filebasename, ext = os.path.splitext(fn)
                    if ext.lower() in exts:
                        allfiles.append(fullurl)
        except Exception as e:
            print ("Error get_all_video_files. ",e.args)
            print('Profile is : ',profile)
        return allfiles
    
    
    def run_cmd(self,cmd):
        try:
            retval = subprocess.Popen(cmd,stdout=subprocess.PIPE)
            stdout_value = retval.communicate()[0]
        except Exception as e:
            print ("Error executing. ",e.args)
            
            
    def get_start_time(self,meta):
        '''catch all possible errors and
        provide a default value'''
        duration = datetime.timedelta(0)
        if meta != 'not' and meta != None and meta.has('duration') != False:
            duration = meta.get('duration')
        return duration
                  
                    
    def make_screen_dir(self,dirname):
        if not os.path.exists(dirname):
            try:
                os.mkdir(dirname) 
            except Exception as e:
                print ("Error make_screen_dir: ",e)
    
    
    def get_unique_urls(self,allfiles):
        alldirs = []
        for file in allfiles:
            dirname = os.path.dirname(file)
            if dirname not in alldirs:
                alldirs.append(dirname)
        return alldirs
    
    
    def delete_screens(self,dirname):
        if os.path.exists(dirname):
            try:
                screens = os.listdir(dirname)
                for screen in screens:
                    screenpath = os.path.join(dirname,screen)
                    os.remove(screenpath)
                    print('Deleting screen',screenpath)
                    
                os.rmdir(dirname)
                print('Deleting dir',dirname)
            except Exception as e:
                print ("Error delete_screens: ",e)

                   
    def get_metadata(self,fullurl):
        metadata = 'not'
        try:
            filename, realname = unicode(fullurl), fullurl
            parser = createParser(filename, realname)
            metadata = extractMetadata(parser)
        except Exception as e:
            print('fullurl : ',fullurl)
            print ("Error getting metadata ",e.args)
        return metadata    
    
         





    def get_config_xml(self):
        script_path = os.path.abspath(os.path.dirname(__file__))
        parent = os.path.normpath(os.path.join(script_path, '..'))
        tree = ET.parse(os.path.join(parent, 'config.xml'))
        return tree


    def get_dirs(self):
        folders = []
        video_folders = self.configxml.find('video_folders')
        for folder in video_folders.getiterator('folder'):
            folders.append(folder.text)
        return folders



    
if __name__ == '__main__':
    Main()
    
    


