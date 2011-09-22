from xml.etree import ElementTree as ET
import Image
import ImageOps
import subprocess
import datetime
import sys
import os
import glob
import time




class Main:
    def __init__(self):
        self.configxml = self.get_config_xml()

        # go !!!
        profiles = self.get_dirs()
        exts = self.configxml.find('video_exts').text.split(',')
        for profile in profiles:
            #self.get_videos_without_screens(profile,exts)
            self.get_screens_without_videos(profile,exts)
            
            
            
    def get_screens_without_videos(self,profile,exts):
        allfiles = self.get_all_video_files(profile, exts)

        screendirs = set()
        for fullurl in allfiles:
            dirname, filename = os.path.split(fullurl)
            screendirs.add(dirname)
            
        for item in screendirs:
            self.check_orphan_screens(os.path.join(item,'screens'))
            
            
            
    def get_videos_without_screens(self,profile,exts):
        allfiles = self.get_all_video_files(profile, exts)

        for fullurl in allfiles:
            hasscreens = self.check_if_has_screens(fullurl)
            if hasscreens == 'no':
                print(fullurl)



    def check_orphan_screens(self,screensdir):
        '''This is not perfect :
        If the name of video is changed but the screen still contains
        the name this will not catch it : 
        
        Example : 

        Star Wars The Clone Wars - S03E07 - Assassin.avi
        renamed to :
        Star Wars The Clone Wars - S03E07 - Assassin - Who.avi
        '''
        
        if os.path.exists(screensdir):
            try:
                screens = []
                for screen in os.listdir(screensdir):
                    screens.append(os.path.splitext(screen)[0])
                    screenfilebasename = os.path.splitext(screen)[0]

                    screen_has_video = 'no'

                    upone = os.path.normpath(os.path.join(screensdir, '..'))
                    for videofile in os.listdir(upone):
                        filebasename = os.path.splitext(videofile)[0]
                        nchars = len(screenfilebasename.replace(filebasename,''))
                        screenlabel = screenfilebasename[:-nchars]
 
                        if screenlabel == filebasename:
                            screen_has_video = 'yes'
                    if screen_has_video == 'no':
                        print(screensdir,screen)
                        self.delete_file(os.path.join(screensdir,screen))
            except Exception as e:
                print ("Error check_if_has_screens: ",e)

    

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



    def get_dirs(self):
        folders = []
        video_folders = self.configxml.find('video_folders')
        for folder in video_folders.getiterator('folder'):
            folders.append(folder.text)
        return folders



    def get_config_xml(self):
        script_path = os.path.abspath(os.path.dirname(__file__))
        parent = os.path.normpath(os.path.join(script_path, '..'))
        tree = ET.parse(os.path.join(parent, 'config.xml'))
        return tree



    def delete_file(self,full_url):
        try:
            if os.path.exists(full_url):
                os.remove(full_url)
                print('Deleting : ',full_url)
        except Exception as e:
            print('Erros deleting : ',e)



if __name__ == '__main__':
    Main()
    
    

