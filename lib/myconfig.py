

class MyConfig:


    def go(self,appPath,commonLib,templatesLib,theXml):
        self.commonLib = commonLib
        self.templatesLib = templatesLib
        
        print ('lib.MyConfig.go')
        
        
        # html = self.writeConfigTabs(theXml.find('configTabs'))
#        html = self.getVideoSettings(theXml.find('video_folders'))
#        return html
        

#        
#    def getVideoSettings(self,xml):
#        wrapper = ET.Element('div')
#        
#        it = xml.getiterator('folder')
#        for folder in it:
#            profileLabel = folder.attrib['profile']
#            profilePath = folder.text
#            n = str(it.index(folder))
#            
#            profile = ET.SubElement(wrapper, "div")
#
#            label = ET.SubElement(profile, "label")
#            label.attrib['for'] = 'vid_'+n
#            label.text = profileLabel
#
#            input = ET.SubElement(profile, "input")
#            input.attrib['id'] = 'vid_'+n
#            input.attrib['type'] = 'text'
#            input.attrib['value'] = profilePath
#            
#            button = ET.SubElement(profile, "button")
#            button.text = 'remove'
#
#        return ET.tostring(wrapper) 
#        
#        
#        
#    def writeConfigTabs(self,xml):
#        wrapper = ET.Element('div')
#        wrapper.attrib['id'] = 'config_tabs_wrapper'
#        
#        it = xml.getiterator('tab')
#        for tab in it:
#            profileLabel = tab.attrib['label']
#            profile = tab.attrib['profile']



