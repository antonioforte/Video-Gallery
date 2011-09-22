from xml.etree import ElementTree as ET
import os
import base64
import pprint

class common:

    def getShortString(self,nC,theStr):
        strOut = ''
        if len(theStr) <= nC:
            strOut = theStr
        else:
            for c in range(0,nC):
                strOut += theStr[c]
            strOut += '...'
        return strOut


    def getXml(self,filename):
        try:
            tree = ET.parse(filename)
            print ("Sucess parsing xml file: ",filename)
            return tree
        except Exception as e:
            print ("Error could not get xml file: ", e)
          
            
    def deleteFile(self,full_url):
        try:
            print ('Lib.common.deleteFile')
            if os.path.exists(full_url):
                os.remove(full_url)
        except Exception as e:
            print ("Error Lib.common.deleteFile : ", e)
          

    def get_locid(self,data):
        a = base64.b64encode(data)
        return a


    def walkDir(self,dir):
        items = []
        try:
            for root,dirs,files in os.walk(unicode(dir)):
                for file in files:
                    full_url = os.path.join(dir,root,file)
                    url, ext = os.path.splitext(full_url)
                    items.append([full_url,ext,file])
        except Exception as e:
            print ("Error Lib.common.walkDir : ", e)
        return items
    

    def print_nice(self,data):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
    
    
    def walkDirFilter(self,dir,exts):
        items = []
        try:
            for root,dirs,files in os.walk(unicode(dir)):
                for file in files:
                    full_url = os.path.join(dir,root,file)
                    url, ext = os.path.splitext(full_url)
                    if ext in exts:
                        items.append([full_url,ext,file])
        except Exception as e:
            print ("Error Lib.common.walkDirFilter : ", e)
        return items
    
    
    def getFileDate(self,full_url):
        fileDate = 'not'
        try:
            fileDate = str(os.path.getmtime(full_url))
        except Exception as e:
            print ("Error Lib.common.getFileDate: ",e)
        return fileDate
    

    def getFileSize(self,full_url):
        fileSize = 0
        try:
            fileSize = str(os.path.getsize(full_url) /1024/1024)
        except Exception as e:
            print ("Error Lib.common.getFileSizeNew: ",e)
        return fileSize 
    

    def getElementById(self,xml,id):
        '''Iterate through all elements in xml
        to find the one with the specified id'''
        theel = 'not'
        for el in xml.getiterator():
            atrbs = el.items() # returns a list of pairs
            for pair in atrbs:
                if pair[0] == 'id' and pair[1] == id:
                    theel = el
        return theel 
    
 
    def writeXMLFile(self,savepath,tagXmlData):
        try:
            #You need to wrap the root element in an Elementtree object, before you can write it:
            ET.ElementTree(tagXmlData).write(savepath, encoding='utf-8')
        except Exception as e:
            print ("Error Lib.common.writeXMLFile. ",e) 

            
    def getDirDirs(self,dir):
        dirs = []
        try:
            for item in os.listdir(unicode(dir)):
                fullpath = os.path.join(dir,item)
                if os.path.isdir(fullpath):
                    dirs.append(item)
        except Exception as e:
            print ("Error Lib.common.getDirDirs : ",e.args[0])   
             
        dirs.sort(cmp=None, key=None, reverse=False)
        return dirs    
            
            
    def checkFile(self,url):
        r = 'no'
        if os.path.exists(url):
            r = 'yes'
        return r    
            

    def prettyPrintET(self,element):
        from xml.dom.minidom import parseString
        txt = ET.tostring(element)
        print (parseString(txt).toprettyxml()) 

