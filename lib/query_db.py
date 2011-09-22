import os
import cPickle
from xml.etree import ElementTree as ET
import templates
import urllib
import common
import time
from PySide import QtCore



class queryDbWorker(QtCore.QThread):
    postBuildDbWorkerSig = QtCore.Signal(str)
        
    def __init__(self, parent = None):
        QtCore.QThread.__init__(self, parent)
        self.exiting = False
        self.lib = common.common() 
        self.templates = templates.templates()


    def __del__(self):
        self.exiting = True


    def set_values(self,curdir,configxml,dbpath,query):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        self.db = self.get_db(self.dbpath)
        
        self.query = query
        self.mode = query[0]
        self.locprofile = query[1]
        self.loclabel = query[2]
        self.locurl = query[3]
        self.locid = self.lib.get_locid(self.locprofile+self.loclabel+self.locurl)



    def run(self):
        '''         
         There two levels: front and afterfront. 
         The front level gets the front html of each profile, this is equal to all profiles.
         The afterfront level is different to each profile.
         '''
        html = 'not'
        
        if self.locprofile == 'Movies':
            if self.mode == 'front':
                html = self.get_front_html()
            if self.mode == 'afterfront':
                html = self.get_movie_html()

        if self.locprofile == 'TV':
            if self.mode == 'front':
                html = self.get_front_html()
            if self.mode == 'afterfront':
                html = self.get_tv_show()

        if self.locprofile == 'Races':
            if self.mode == 'front':
                html = self.get_front_html()
            if self.mode == 'afterfront':
                html = self.get_races_season()

        self.postBuildDbWorkerSig.emit(html)

        
        
        
    def get_front_html(self):
        ''' Get front page of all profils'''
        html = self.get_common_html()
        body = html.find('body')

        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['id'] = 'frontWrapper'
        
        data = self.db[self.locid]['data']
        for movie in sorted(data.keys()):

            div = ET.SubElement(wrapper,'div')
            div.attrib['class'] = 'movieWrapper'
            div.attrib['data-movie_label'] = movie
            
            # get image 
            img = ET.SubElement(div,'img')
            img.attrib['class'] = 'movieWrapperCover'
            if data[movie]['hasSmallPic'] == 'yes':
                img.attrib['src'] = 'file://' + os.path.join(self.locurl, movie, 'folder.jpg')
            else:
                # only gets screen from screens folder when its in movie mode
                # because the other modes have one nested folder
                has_screen = self.get_movie_screen(os.path.join(self.locurl, movie))
                if has_screen[0] == 'yes':
                    img.attrib['src'] = 'file://' + has_screen[1] 
                else:
                    img.attrib['src'] = 'file://'+os.path.join(self.curdir, 'res', 'graphics', 'default_200x100.png')

            span = ET.SubElement(div,'span')
            span.attrib['data-label'] = movie
            span.text = self.lib.getShortString(20,movie)

        return ET.tostring(html)
        
        
        
        
    def get_movie_screen(self,url):
        has_screen = ['not','not']
        screensdir = os.path.join(url,'screens')

        if os.path.exists(screensdir):
            screens = os.listdir(screensdir)
            if len(screens) != 0:
                has_screen[0] = 'yes'
                has_screen[1] = os.path.join(url,'screens',screens[5])
                
        return has_screen
        
        

        
        
        
        

    


    def get_movie_html(self):
        html = self.get_common_html()
        body = html.find('body')

        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['class'] = 'listWrapper'
        
        movie = self.query[4]
        data = self.db[self.locid]['data'][movie]

        div = ET.SubElement(wrapper,'div')
        div.attrib['class'] = 'listItemWrapper'
        
        div_after_pic = ET.SubElement(div,'div',{'class':'divAfterPic'})  
        span = ET.SubElement(div_after_pic,'span',{'class':'spanSeasonNumber'})
        
        span_show_storyboard = ET.SubElement(div_after_pic,'span',{'class':'spanShowStoryboard'})
        span_show_storyboard.text = 'storyboard'
        
        span_show_episodes = ET.SubElement(div_after_pic,'span',{'class':'spanShowEpisodes'})
        span_show_episodes.text = 'files'
        span.text = movie

        img = ET.SubElement(div,'img')
        img.attrib['class'] = 'movieBigWrapperCover'
        if data['hasBigPic'] == 'yes':
            img.attrib['src'] = 'file://'+os.path.join(self.locurl,movie,'folder_big.jpg')
        else:
            img.attrib['src'] = 'file://'+os.path.join(self.curdir, 'res', 'graphics', 'default_720x200.png')

        filestable = self.get_files_table(data['files'])
        div.append(filestable)

        return ET.tostring(html)







    def get_tv_show(self):
        html = self.get_common_html()
        body = html.find('body')

        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['class'] = 'listWrapper'
        
        show = self.query[4]
        data = self.db[self.locid]['data'][show]
        seasons = data['seasons']

        for season in sorted(seasons.keys()):
            div = ET.SubElement(wrapper,'div')
            div.attrib['class'] = 'listItemWrapper'
            
            div_after_pic = ET.SubElement(div,'div',{'class':'divAfterPic'})
            span = ET.SubElement(div_after_pic,'span',{'class':'spanSeasonNumber'})
            span.text = season
            
            span_show_storyboard = ET.SubElement(div_after_pic,'span',{'class':'spanShowStoryboard'})
            span_show_storyboard.text = 'storyboard'
            
            span_show_episodes = ET.SubElement(div_after_pic,'span',{'class':'spanShowEpisodes'})
            span_show_episodes.text = 'episodes'

            img = ET.SubElement(div,'img')
            img.attrib['class'] = 'movieBigWrapperCover'
            if seasons[season]['hasBigPic'] == 'yes':
                img.attrib['src'] = 'file://'+os.path.join(self.locurl,show,season,'folder_big.jpg')
            else:
                img.attrib['src'] = 'file://'+os.path.join(self.curdir, 'res', 'graphics', 'default_720x200.png')

            filestable = self.get_files_table(seasons[season]['files'])
            div.append(filestable)

        return ET.tostring(html)




    def get_races_season(self):
        html = self.get_common_html()
        body = html.find('body')

        wrapper = ET.SubElement(body, 'div')
        wrapper.attrib['class'] = 'listWrapper'

        season = self.query[4]
        data = self.db[self.locid]['data'][season]
        races = data['races']

        for race in sorted(races.keys()):
            div = ET.SubElement(wrapper,'div')
            div.attrib['class'] = 'listItemWrapper'
        
            div_after_pic = ET.SubElement(div,'div',{'class':'divAfterPic'})
            span = ET.SubElement(div_after_pic,'span',{'class':'spanSeasonNumber'})
            span.text = race
            
            span_show_storyboard = ET.SubElement(div_after_pic,'span',{'class':'spanShowStoryboard'})
            span_show_storyboard.text = 'storyboard'
            
            span_show_episodes = ET.SubElement(div_after_pic,'span',{'class':'spanShowEpisodes'})
            span_show_episodes.text = 'files'

            img = ET.SubElement(div,'img')
            img.attrib['class'] = 'movieBigWrapperCover'
            if races[race]['hasBigPic'] == 'yes':
                img.attrib['src'] = 'file://'+os.path.join(self.locurl,season,race,'folder_big.jpg')
            else:
                img.attrib['src'] = 'file://'+os.path.join(self.curdir, 'res','graphics', 'default_720x200.png')

            filestable = self.get_files_table(races[race]['files'])
            div.append(filestable)

        return ET.tostring(html)






    def get_files_table(self, files):
        table = ET.Element('table',{'class':'videoFilesTable'})
        
        for fullurl in sorted(files.keys()):
            url, filename = os.path.split(fullurl)
            name, ext = os.path.splitext(filename)
            
            tr = ET.SubElement(table, 'tr')
            
            # 1st cell
            td9 = ET.SubElement(tr, 'td')
            img = ET.SubElement(td9,'img')
            img.attrib['class'] = 'fileScreen'
            img.attrib['data-url'] = fullurl
            hasscreen = self.lib.checkFile(os.path.join(url,'screens',name+' - 2.jpg'))
            if hasscreen == 'yes':
                img.attrib['src'] = 'file://'+os.path.join(url,'screens',urllib.quote(name+' - 2.jpg'))
            else:
                img.attrib['src'] = 'file://'+os.path.join(self.curdir, 'res', 'graphics', 'default_200x100.png')

            # 2nd cell
            td0 = ET.SubElement(tr, 'td')
            td0.text = name

            # 3th cell
            td1 = ET.SubElement(tr, 'td')
            
            span1 = ET.SubElement(td1, 'span')
            span1.text = str(files[fullurl]['width'])+'x'+str(files[fullurl]['height'])

            span2 = ET.SubElement(td1, 'span')
            duration = time.strftime('%H:%M:%S', time.gmtime(files[fullurl]['duration']))
            span2.text = duration
            
            span3 = ET.SubElement(td1, 'span')
            date = time.strftime('%Y-%m-%d',time.gmtime(float(files[fullurl]['date'])))
            span3.text = date
            
            span4 = ET.SubElement(td1, 'span')
            span4.text = files[fullurl]['hasSubs']
            
            span4 = ET.SubElement(td1, 'span')
            span4.text = str(files[fullurl]['size'])+' mb'
            
            span6 = ET.SubElement(td1, 'span')
            span6.text = ext
            
            # 4rd cell
            tdplayers = ET.SubElement(tr, 'td')
            players = self.configxml.find('video_players')
            for player in players.getiterator('app'):
                s = ET.SubElement(tdplayers, 'span')
                s.attrib['data-video_url'] = fullurl
                s.attrib['data-app'] = player.text
                s.attrib['class'] = 'video_launcher'
                s.text = player.text
        return table



        

    def get_db(self,dbpath):
        data = cPickle.load(open(dbpath, 'rb'))
        return data
    
    
    
    def get_common_html(self):
        html = ET.Element('html')
        head = ET.SubElement(html, 'head')
        
        meta = ET.SubElement(head, 'meta')
        meta.attrib['http-equiv'] = 'content-type'
        meta.attrib['content'] = 'text/html; charset=utf-8'
        
        style = ET.SubElement(head, 'link')
        style.attrib['rel'] = 'stylesheet'
        style.attrib['type'] = 'text/css'
        style.attrib['href'] = 'file://' + os.path.join(self.curdir, 'site', 'style.css')
        
        script2 = ET.SubElement(head, 'script')
        script2.attrib['type'] = 'text/javascript'
        script2.attrib['src'] = 'file://' + os.path.join(self.curdir, 'site', 'js', 'dom_helper.js')
        script2.text = '/*nonsense*/'
        
        script3 = ET.SubElement(head, 'script')
        script3.attrib['type'] = 'text/javascript'
        script3.attrib['src'] = 'file://' + os.path.join(self.curdir, 'site', 'js', 'navletters.js')
        script3.text = '/*nonsense*/'
        
        script1 = ET.SubElement(head, 'script')
        script1.attrib['type'] = 'text/javascript'
        script1.attrib['src'] = 'file://' + os.path.join(self.curdir, 'site', 'js', 'common.js')
        script1.text = '/*nonsense*/'
        
        title = ET.SubElement(head, 'title')
        title.text = self.loclabel
        
        body = ET.SubElement(html, 'body')
        body.attrib['data-profile'] = self.locprofile
        body.attrib['data-label'] = self.loclabel
        body.attrib['data-url'] = self.locurl
        body.attrib['data-mode'] = self.mode
        return html  
    
    
    
#        for item in self.data.keys():
#            print('after',self.data[item]['data'].keys())

#        for k, v in data.iteritems():
#            print('shit',k,v)

#        self.lib.print_nice(movie)
#        print('et dump',ET.tostring(html))
#        self.lib.prettyPrintET(html)




class queryDb(QtCore.QObject):
    postQueryDbSig = QtCore.Signal(str)
    startQueryDbSig = QtCore.Signal(str)
    endQueryDbSig = QtCore.Signal(str)

    @QtCore.Slot(str,str,str,str,str,str)
    def go(self,*args):
        self.theargs = args
        self.worker = queryDbWorker()
        self.worker.set_values(self.curdir,self.configxml,self.dbpath,args)
        self.worker.finished.connect(self.say_end)
        
        # Commenting this because it is causing a flash
        # self.worker.started.connect(self.say_start)
        self.worker.postBuildDbWorkerSig.connect(self.post_html)
        self.worker.start()


    def set_values(self,curdir,configxml,dbpath):
        self.curdir = curdir
        self.configxml = configxml
        self.dbpath = dbpath
        

    def say_end(self):
        self.endQueryDbSig.emit('End query')


    def say_start(self):
        html = ET.Element('html')
        head = ET.SubElement(html, 'head')
        
        meta = ET.SubElement(head, 'meta')
        meta.attrib['http-equiv'] = 'content-type'
        meta.attrib['content'] = 'text/html; charset=utf-8'
        
        style = ET.SubElement(head, 'link')
        style.attrib['rel'] = 'stylesheet'
        style.attrib['type'] = 'text/css'
        style.attrib['href'] = 'file://' + os.path.join(self.curdir, 'site', 'style.css')
        
        goback = ET.SubElement(html,'div', {'id':'goback'})
        span = ET.SubElement(goback,'span', {'class':'novisibility'})
        span.text = 'iamherejustforshow'
        
        div = ET.SubElement(html,'div',{'class':'loadingDiv'})
        for item in self.theargs:
            div2 = ET.SubElement(div, 'div')
            div2.text = item
        
        self.startQueryDbSig.emit(ET.tostring(html))
        
        
    def post_html(self,html):
        self.postQueryDbSig.emit(html)

        
        
        
        
        
        
        
        
        
        
