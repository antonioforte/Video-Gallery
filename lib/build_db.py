import os
import cPickle
import json
from xml.etree import ElementTree as ET
from hachoir_parser import createParser
from hachoir_metadata import extractMetadata
import templates
import common
from PySide import QtCore



class buildDbWorker(QtCore.QThread):
    postBuildDbWorkerSig = QtCore.Signal(str)
        
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.lib = common.common() 
        self.templates = templates.templates()


    def __del__(self):
        self.exiting = True


    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        self.video_folders = self.configxml.find('video_folders')
        self.exts = self.configxml.find('video_exts').text


    def run(self):
        # global dict
        data = {}

        # for each location
        locs = self.video_folders.getiterator('folder')
        for loc in locs:
            i = locs.index(loc)
            
            loclabel = loc.attrib['label']
            locprofile = loc.attrib['profile']
            locurl = loc.text
            locid = self.lib.get_locid(locprofile+loclabel+locurl)

            # create dict with location details
            # the data key holds files found
            data[locid] = {}
            data[locid]['label'] = loclabel
            data[locid]['profile'] = locprofile
            data[locid]['url'] = locurl
            data[locid]['data'] = self.scan_folders(loclabel,locprofile,locurl)

            self.send_update_signal(data[locid],i,locs)
        self.savedb(data)
        #self.lib.print_nice(data)


    def send_update_signal(self,data,i,locs):
        ul = ET.Element('ul')
        li1 = ET.SubElement(ul, 'li')
        li1.text = 'Searching: '+str(i+1)+' of '+str(len(locs))
        
        li5 = ET.SubElement(ul, 'li')
        li5.text = 'Found: '+str(len(data['data']))
        
        li2 = ET.SubElement(ul, 'li')
        li2.text = 'Profile: '+data['profile']

        li3 = ET.SubElement(ul, 'li')
        li3.text = 'Label: '+data['label']
        
        li4 = ET.SubElement(ul, 'li')
        li4.text = 'Url: '+data['url']

        li6 = ET.SubElement(ul, 'li')
        li6.text = '-----------------'

        self.postBuildDbWorkerSig.emit(ET.tostring(ul))
        
        


    def scan_folders(self,loclabel,locprofile,locurl):
        data = {}
        if locprofile == 'Movies':
            data = self.get_movies(locurl)
        if locprofile == 'TV':
            data = self.get_tv(locurl)
        if locprofile == 'Races':
            data = self.get_races(locurl)
        return data
            
            
            
    def get_movies(self,locurl):   
        data = {}       

        movies = self.lib.getDirDirs(locurl)
        for movie in movies:
            data[movie] = {}
            data[movie]['hasDesc'] = self.lib.checkFile(os.path.join(locurl,movie, 'desc.txt'))  
            data[movie]['hasSmallPic'] = self.lib.checkFile(os.path.join(locurl,movie, 'folder.jpg')) 
            data[movie]['hasBigPic'] = self.lib.checkFile(os.path.join(locurl,movie, 'folder_big.jpg')) 
            data[movie]['files'] = {}

            videofiles = self.lib.walkDirFilter(os.path.join(locurl,movie),self.exts)
            for file in videofiles:
                full_url = file[0]
                ext = file[1]
                filename = file[2]
                # this is costing scanning time
                meta = self.get_metadata(full_url)
                
                data[movie]['files'][full_url] ={}
                data[movie]['files'][full_url]['size'] = self.lib.getFileSize(full_url)
                data[movie]['files'][full_url]['date'] = self.lib.getFileDate(full_url)
                data[movie]['files'][full_url]['hasSubs'] = self.lib.checkFile(full_url.replace(ext,'.srt'))  
                
                data[movie]['files'][full_url]['duration'] = self.get_duration_seconds(meta)
                data[movie]['files'][full_url]['width'] = self.get_metadata_entry(meta,'width')
                data[movie]['files'][full_url]['height'] = self.get_metadata_entry(meta,'height')

        return data
    


    def get_tv(self,locurl):
        data = {}   
        
        # get shows
        shows = self.lib.getDirDirs(locurl)
        for show in shows:
            data[show] = {}
            data[show]['hasDesc'] = self.lib.checkFile(os.path.join(locurl,show, 'desc.txt'))  
            data[show]['hasSmallPic'] = self.lib.checkFile(os.path.join(locurl,show, 'folder.jpg')) 
            data[show]['hasBigPic'] = self.lib.checkFile(os.path.join(locurl,show, 'folder_big.jpg')) 
            data[show]['seasons'] = {}

            # get seasons
            seasons = self.lib.getDirDirs(os.path.join(locurl,show))
            for season in seasons:
                data[show]['seasons'][season] = {}
                data[show]['seasons'][season]['hasDesc'] = self.lib.checkFile(os.path.join(locurl,show,season,'desc.txt'))  
                data[show]['seasons'][season]['hasSmallPic'] = self.lib.checkFile(os.path.join(locurl,show,season,'folder.jpg')) 
                data[show]['seasons'][season]['hasBigPic'] = self.lib.checkFile(os.path.join(locurl,show,season,'folder_big.jpg')) 
                data[show]['seasons'][season]['files'] = {}
                
                # get files
                videofiles = self.lib.walkDirFilter(os.path.join(locurl,show,season),self.exts)
                for file in videofiles:
                    full_url = file[0]
                    ext = file[1]
                    filename = file[2]
                    # this is costing scanning time
                    meta = self.get_metadata(full_url)
                    
                    data[show]['seasons'][season]['files'][full_url] ={}
                    data[show]['seasons'][season]['files'][full_url]['size'] = self.lib.getFileSize(full_url)
                    data[show]['seasons'][season]['files'][full_url]['date'] = self.lib.getFileDate(full_url)
                    data[show]['seasons'][season]['files'][full_url]['hasSubs'] = self.lib.checkFile(full_url.replace(ext,'.srt'))  
                    
                    data[show]['seasons'][season]['files'][full_url]['duration'] = self.get_duration_seconds(meta)
                    data[show]['seasons'][season]['files'][full_url]['width'] = self.get_metadata_entry(meta,'width')
                    data[show]['seasons'][season]['files'][full_url]['height'] = self.get_metadata_entry(meta,'height')

        return data



    def get_races(self,locurl):
        '''Lots of repeated code i know.
        This will be extended to add more things.
            - picture of circuit
            - diagram of circuit
            - winner, podium
        '''
        data = {}   
        
        # get seasons
        seasons = self.lib.getDirDirs(locurl)
        for season in seasons:
            data[season] = {}
            data[season]['hasDesc'] = self.lib.checkFile(os.path.join(locurl,season, 'desc.txt'))  
            data[season]['hasSmallPic'] = self.lib.checkFile(os.path.join(locurl,season, 'folder.jpg')) 
            data[season]['hasBigPic'] = self.lib.checkFile(os.path.join(locurl,season, 'folder_big.jpg')) 
            data[season]['races'] = {}

            # get races
            races = self.lib.getDirDirs(os.path.join(locurl,season))
            for race in races:
                data[season]['races'][race] = {}
                data[season]['races'][race]['hasDesc'] = self.lib.checkFile(os.path.join(locurl,season,race,'desc.txt'))  
                data[season]['races'][race]['hasSmallPic'] = self.lib.checkFile(os.path.join(locurl,season,race,'folder.jpg')) 
                data[season]['races'][race]['hasBigPic'] = self.lib.checkFile(os.path.join(locurl,season,race,'folder_big.jpg')) 
                data[season]['races'][race]['files'] = {}
                data[season]['races'][race]['mysnaps'] = []
                
                # get mysnaps
                mysnaps = self.lib.walkDir(os.path.join(locurl,season,race,'mysnaps'))
                for snap in mysnaps:
                    data[season]['races'][race]['mysnaps'].append(snap[2])

                # get files
                videofiles = self.lib.walkDirFilter(os.path.join(locurl,season,race),self.exts)
                for file in videofiles:
                    full_url, ext, filename = file[0], file[1], file[2]

                    # this is costing scanning time
                    meta = self.get_metadata(full_url)
                    
                    data[season]['races'][race]['files'][full_url] ={}
                    data[season]['races'][race]['files'][full_url]['size'] = self.lib.getFileSize(full_url)
                    data[season]['races'][race]['files'][full_url]['date'] = self.lib.getFileDate(full_url)
                    data[season]['races'][race]['files'][full_url]['hasSubs'] = self.lib.checkFile(full_url.replace(ext,'.srt'))  
                    
                    data[season]['races'][race]['files'][full_url]['duration'] = self.get_duration_seconds(meta)
                    data[season]['races'][race]['files'][full_url]['width'] = self.get_metadata_entry(meta,'width')
                    data[season]['races'][race]['files'][full_url]['height'] = self.get_metadata_entry(meta,'height')

        return data



    def get_duration_seconds(self,meta):
        secs = 0
        duration = self.get_metadata_entry(meta,'duration')
        try:
            if duration.seconds != 0:
                secs = duration.seconds
        except Exception as e:
            print ("Error getting duration ",e.args)
        return secs


    def get_metadata(self,fullurl):
        metadata = 'not'
        try:
            filename, realname = unicode(fullurl), fullurl
            parser = createParser(filename, realname)
            metadata = extractMetadata(parser)
        except Exception as e:
            print ("Error getting metadata ",e.args)
        return metadata   

    
    def get_metadata_entry(self,meta,field):
        entry = 'not'
        try:
            entry = meta.get(field)
        except Exception as e:
            print ("Error get_metadata_entry ",e.args)
        return entry



    def savedb(self,data):
        cPickle.dump(data, open(self.dbpath, 'wb'),-1)
        
        a = json.dumps(data,indent=4)
        b = open(self.dbpath+'.json', 'w')
        b.write(a)
        b.close()







class buildDb(QtCore.QObject):
    postBuildDbSig = QtCore.Signal(str)
    startBuildDbSig = QtCore.Signal(str)
    endBuildDbSig = QtCore.Signal(str)

    @QtCore.Slot()
    def go(self):
        self.worker = buildDbWorker()
        self.worker.set_values(self.curdir,self.configxml,self.dbpath)
        self.worker.finished.connect(self.say_end)
        self.worker.started.connect(self.say_start)
        self.worker.postBuildDbWorkerSig.connect(self.post_html)
        self.worker.start()


    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        

    def say_end(self):
        self.endBuildDbSig.emit('End scanning')


    def say_start(self):
        self.startBuildDbSig.emit('Started scanning')
        
        
    def post_html(self,html):
        self.postBuildDbSig.emit(html)

        
        
        
        
        
        
        
        
        
        