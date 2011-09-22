from xml.etree import ElementTree as ET
import Image
import ImageOps
import sys
import os
import time
import random
import itertools


'''storyboard = folder_big.jpg
create storyboard in folder of video file
'''

class Main:
    def __init__(self):
        print('----------------------------------')
        print('Create storyboard start')
        self.configxml = self.get_config_xml()
        self.curdir = os.path.abspath(os.path.dirname(__file__))
        
        self.delete_existing_folderbig = self.configxml.find('delete_existing_folderbig').text
        self.columns = int(self.configxml.find('folderbigcolumns').text)
        self.rows = int(self.configxml.find('folderbigrows').text)
        self.vsep = int(self.configxml.find('folderbigvsep').text)
        self.hsep = int(self.configxml.find('folderbighsep').text)
        self.imagewidth = int(self.configxml.find('folderbigthumbwidth').text)
        self.imageheight = int(self.configxml.find('folderbigthumbheight').text)
        
        self.totalfolderbig = 0
        self.dirswithoutfolderbig = []
        begin_time = time.time()

        # go !!!
        profiles = self.get_dirs()
        #profiles = ['/media/vault_big/video/TESTING']
        exts = self.configxml.find('video_exts').text.split(',')
        for profile in profiles:
            self.run(profile,exts)
            
            
        print('-------------------------------------')
        for item in self.dirswithoutfolderbig:
            print('no folder big',item)
        total_time = time.strftime("%H:%M:%S", 
                           time.gmtime(time.time() - begin_time))
        print('time taken',total_time)
        print('total folder big',self.totalfolderbig)
        print('the end')
        print('-------------------------------------')
        
        
            
    def run(self,profile,exts):
        allfiles = self.get_all_video_files(profile, exts)
        for uniqueurl in self.get_unique_urls(allfiles):
            folderbigpath = os.path.join(uniqueurl,'folder_big.jpg')
            screensdir = os.path.join(uniqueurl,'screens')
            hasscreensdir = os.path.exists(screensdir)
            hasfolderbig = os.path.exists(folderbigpath)
            
            if hasscreensdir:
                if not hasfolderbig or self.delete_existing_folderbig == 'yes':
                    screens = os.listdir(screensdir)
                    self.create_big_image(screensdir,screens,folderbigpath)
            if not hasscreensdir:
                self.dirswithoutfolderbig.append(uniqueurl)
                
                
                
    def create_big_image(self,screensdir,screens,folderbigpath):
        # http://stackoverflow.com/questions/3907443/python-pil-missing-images
        COLUMNS=self.columns
        ROWS=self.rows
        VSEP=self.vsep
        HSEP=self.hsep
        IMAGE_SIZE=(self.imagewidth,self.imageheight)
        NUMBERTHUMBS = ROWS * COLUMNS 
        
        image=Image.new("RGB",
                        ((IMAGE_SIZE[0]+HSEP)*COLUMNS+HSEP,
                         (IMAGE_SIZE[1]+VSEP)*ROWS+VSEP),
                        (0,0,0))

        i = 0
        pilscreens = self.get_pilscreens(screens,screensdir,NUMBERTHUMBS,IMAGE_SIZE)
        for row,column in itertools.product(range(ROWS),range(COLUMNS)):
            #print(row,column)
            paste_x = HSEP+column*(IMAGE_SIZE[0]+HSEP)
            paste_y = VSEP+row*(IMAGE_SIZE[1]+VSEP)
            image.paste(pilscreens[i],(paste_x,paste_y))
            i += 1
            
        try:
            image.save(folderbigpath, "JPEG")
            self.totalfolderbig += 1
            print ('Saving image',folderbigpath)
        except Exception as e:
            print ('Error saving image: ',e) 
            
            
            
    def get_pilscreens(self,screens,screensdir,number_thumbs,image_size):
        method = Image.ANTIALIAS
        bleed = 0
        centering = (0.5,0.5)
        
        defaulthumbpath = self.get_defaulthumbpath()
        defaulthumb = ImageOps.fit(Image.open(defaulthumbpath),image_size,method,bleed,centering)
        pilscreens = [defaulthumb] * number_thumbs
        
        #random.shuffle(screens)
        i = 0
        for screen in screens:
            if i < number_thumbs:
                im = Image.open(os.path.join(screensdir,screen))
                thumb = ImageOps.fit(im,image_size,method,bleed,centering)
                pilscreens[i] = thumb
                i += 1
        return pilscreens



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

     
    def get_unique_urls(self,allfiles):
        alldirs = []
        for file in allfiles:
            dirname = os.path.dirname(file)
            if dirname not in alldirs:
                alldirs.append(dirname)
        return alldirs    
            
            
    def get_config_xml(self):
        script_path = os.path.abspath(os.path.dirname(__file__))
        parent = os.path.normpath(os.path.join(script_path, '..'))
        tree = ET.parse(os.path.join(parent, 'config.xml'))
        return tree


    def get_defaulthumbpath(self):
        script_path = os.path.abspath(os.path.dirname(__file__))
        parent = os.path.normpath(os.path.join(script_path, '..'))
        defaulthumbpath = os.path.join(parent,'res','graphics','default_thumb_folderbig.png')
        return defaulthumbpath
    
    
    def get_dirs(self):
        folders = []
        video_folders = self.configxml.find('video_folders')
        for folder in video_folders.getiterator('folder'):
            folders.append(folder.text)
        return folders
    
    


    
if __name__ == '__main__':
    Main()
    
    


            
            
