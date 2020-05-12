from html.parser import HTMLParser
import unicodedata as ucd

cat2cat = {
    'Lo': 'dev',
    'Mc': 'dev',
    'Mn': 'dev',
    'Ll': 'L',
    'Lu': 'L'
}

def splitData(data):
    word = ''
    cat = ''
    for a in data:
        nc = ucd.category(a)
        if nc in cat2cat: nc = cat2cat[nc]
        if cat=='':
            cat = nc
            word = a
        elif cat!=nc:
            if len(word)>0:
                yield word, cat
                word=''
            cat = nc
            word = a
        else:
            word += a
    if len(word)>0:
        yield word, cat

class HtmlScanResult(HTMLParser):

    def initScan(self):
        self.Title = ''
        self.Status = []
        self.Line = []
        self.Lines = []
        self.TitleCatch = False
        self.TagCounter = {
            'p': -1,
            'h1': -1,
            'h2': -1,
            'h3': -1,
            'div': -1,
            'td': -1,
            'body': 0
        }
        self.CurrentTag = 'body'

    def handle_starttag(self, tag, attrs):
        if tag=='title':
            self.AddStatus(tag)
            self.TitleCatch=True
        elif (tag=='h1' or tag=='h2' or tag=='h3') and len(self.Title)==0:
            self.TitleCatch=True
            self.FlushLine()
            self.TagCounter[tag] = self.TagCounter[tag]+1
            self.CurrentTag=tag
        elif tag=='script':
            self.FlushLine()
            self.AddStatus(tag)
        elif tag=='div' or tag=='p' or tag=='td':
            self.FlushLine()
            self.TagCounter[tag] = self.TagCounter[tag]+1
            self.CurrentTag=tag

    def handle_endtag(self, tag):
        if tag == "title":
            self.TitleCatch=False
            self.RemoveStatus(tag)
        elif tag=='script':
            self.RemoveStatus(tag)
        elif tag=='p' or tag=='body':
            self.FlushLine()
        elif (tag=='h1' or tag=='h2' or tag=='h3') and self.TitleCatch==True:
            self.FlushLine()
            self.TitleCatch=False

    def handle_data(self, data):
        data = data.strip()
        if len(data)==0:
            #print ('Whitespaces')
            return
        #print("Encountered some data  :", data)
        #words = data.split()
        for word,cat in splitData(data):
            #cls = clasiffyWord(word)
            #if cls.find('-')>0 or cls=='gen':
            if cat=='Nd' or cat=='L':
                self.AppendWord(word)
                #print('T', word.strip(), cat)
#                for a in word:
#                    print("  [", a, ']', ord(a), ucd.decomposition(a))
#        pass


    def AddStatus(ws,status):
        if ws.Status == None:
            ws.Status = []
        ws.Status.append(status)

    def RemoveStatus(ws,status):
        if ws.Status == None:
            return
        b = True
        while b:
            L = len(ws.Status)
            if L > 0:
                if ws.Status[L-1] == status:
                    b = False
                ws.Status = ws.Status[:L-1]
            else:
                b = False

    def HasLastStatus(ws,status):
        if ws.Status != None and len(ws.Status) > 0:
            return ws.Status[len(ws.Status)-1] == status
        return False

    def AppendWord(ws,word):
        if ws.TitleCatch:
            if len(ws.Title) > 0:
                ws.Title += " "
            ws.Title += word
        elif ws.HasLastStatus("script"):
            pass
        else:
            if ws.Line == None:
                ws.Line = []
            ws.Line.append(word)

    def FlushLine(ws):
        if ws.Lines == None:
            ws.Lines = []
        if ws.Line != None and len(ws.Line) > 0:
            ws.Lines.append({'line':ws.Line, 'tag': ws.CurrentTag, 'num': ws.TagCounter[ws.CurrentTag] })
            ws.Line = []
