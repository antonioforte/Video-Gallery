



class srtEntry(object):
    def __init__(self, entry):
        # ['3\n', '00:01:14,211 --> 00:01:16,911\n', 'text\n']
        utf8bom = '\xef\xbb\xbf'

        self.index = int(entry[0].lstrip(utf8bom))
        start, arrow, end = entry[1].split()
        self.start = self.parsetime(start)
        self.end = self.parsetime(end)
        self.lines = entry[2:]


    def parsetime(self,timestr):
        timestr = timestr.replace(',',':')
        hours, minutes, seconds, miliseconds = timestr.split(':')
        
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        miliseconds = int(miliseconds)
        
        milis = (hours*3600000)+(minutes*60000)+(seconds*1000)+miliseconds
        return milis
    
    
    
class getSubtitles():
    def __init__(self,subfile):
        self.subfile = subfile
        self.entries = self.go()
        
        
    def go(self):
        newlines = ['\n','\r\n','\r']
        entry = []
        entries = []
        thefile = open(self.subfile,'r')

        for line in thefile:
            if line in newlines:
                try:
                    entries.append(srtEntry(entry))
                except Exception as e:
                    print('Could not get srt entry',e)
                entry = []
            else:
                entry.append(line)
                
        thefile.close()
        return entries
    
    
# test 
#entries = getSubtitles('/home/antonio/Dev/python/debulha/my_debulha/Subtitles/samplesubs/Alice in Wonderland.srt')
#for item in entries.entries:
#    print('******************************')
#    print(item)
#    print(item.index)
#    print(item.start)
#    print(item.end)
#    print(item.lines)  
    
    
    
    
    