

class templates:

    def MainIndex(self,curdir,title):
        string = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/xml; charset=utf-8" />
<link href="file://'''+curdir+'''/style.css" rel="stylesheet" type="text/css" />
<tagToBeReplacedBecauseOfFuckingHtmlScriptTags shit="true" />
<title>'''+title+'''</title>
</head>
<body>

<div id="goback">
    <a href=".buildDatabase" class="floatRight">refresh</a>
    <a href=".showFrontPage">Home</a>
</div>


<div id="indexWrapper"></div>

<div id="results">not</div>

</body></html>'''

        return string  


    def Page(self,curdir,title,id):
        string = '''<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/xml; charset=utf-8" />
<link href="file://'''+curdir+'''/style.css" rel="stylesheet" type="text/css" />
<tagToBeReplacedBecauseOfFuckingHtmlScriptTags shit="true" />
<title>'''+title+'''</title>
</head>
<body>
<div id="goback">
    <a href=".showFrontPage">Home</a>
</div>
<div id="'''+id+'''"></div>
</body></html>'''

        return string
    