from os import listdir
import os.path
import io
import json

import query
import html_scan as hs

def EnumerateDir(dir):
    if os.path.isfile(dir):
        if dir.endswith('.htm') or dir.endswith('.html'):
            yield dir
    else:
        for f in listdir(dir):
            full = os.path.join(dir,f)
            if os.path.isfile(full):
                if f.endswith('.htm') or f.endswith('.html'):
                    yield full
            else:
                for i in EnumerateDir(full):
                    yield i

HLNone = 0
HLNormal = 1
HLBold = 2

# def SearchInPara(ta []string, vq *QueryToken, boldStart string, boldEnd string) string {
def SearchInPara(ta,vq,boldStart,boldEnd):
    vq.Reset()
    result = ""
    for index, word in enumerate(ta):
        vq.Match(word, index)
    #print(ta)
    #print(vq.Positions)
    #vq.Print(1)
    if len(vq.Positions) <= 0:
        return None

    tan = [HLNone] * len(ta)
    vq.Projection(tan)
    #print(tan)
    last = HLNone
    for i in range(len(tan)):
        if tan[i] != 0:
            if i > 0 and last == HLNone:
                result += "..."
            elif last != 0:
                result += " "
            if tan[i] == HLBold:
                result += boldStart
            result += ta[i]
            if tan[i] == HLBold:
                result += boldEnd
        else:
            if last != HLNone:
                result += "... "
        last = tan[i]
    #print(result)
    return result


class SearchHistoryClass:
    def __init__(self):
        self.history=[]
        self.currentIndex=0

    def Search(self,query):
        for index,a in enumerate(self.history):
            if a.query==query:
                self.currentIndex=index
                return self.history[index].jsonData()
        new_search = CurrentSearchClass(query)
        self.history.insert(0,new_search)
        return new_search.jsonData()

    def PrevPage(self):
        if len(self.history)==0:
            return ''
        return self.history[self.currentIndex].PrevPage()

    def NextPage(self):
        if len(self.history)==0:
            return ''
        return self.history[self.currentIndex].NextPage()

    def CurrentInfo(self):
        if len(self.history)==0:
            return {
                'currentPage': 0,
                'topPage': -1,
                'canGoBack': False,
                'canGoForward': False
            }
        else:
            cp = self.history[self.currentIndex]
            return {
                'currentPage': cp.currPage,
                'topPage': cp.pageCount(),
                'canGoBack': cp.CanPrevPage(),
                'canGoForward': cp.CanNextPage()
            }

class CurrentSearchFileClass:
    def __init__(self,fileName,title):
        self.fileName=fileName
        self.data=[]
        self.title=title
    def add(self,d):
        self.data.append(d)
    def html(self):
        buffer = io.StringIO()
        self.writeTo(buffer)
        return buffer.getvalue()

    def writeTo(self,buffer):
        buffer.write('<div style=\'background-color:#ffce33;padding-bottom:8px;padding-top:8px;\'>\n')
        if len(self.title) > 0:
            buffer.write("<h3>")
            buffer.write( self.title)
            buffer.write( "</h3>")
            fpn=True
        buffer.write( "<b><a href=\"")
        buffer.write( self.fileName)
        buffer.write( "\">")
        buffer.write( self.fileName)
        buffer.write( "</a></b><br>")
        buffer.write('</div>\n')
        for d in self.data:
            buffer.write('<hr>\n')
            buffer.write(d)


class CurrentSearchClass:
    def __init__(self,query=None):
        self.pages = []
        self.query=query
        self.currPage = 0
        if query!=None:
            self.SearchText(query)

    def CanPrevPage(self):
        return self.currPage > 0

    def CanNextPage(self):
        return self.currPage < len(self.pages)-1

    def PrevPage(self):
        if self.CanPrevPage():
            return self.jsonData(page=self.currPage-1)
        return ''

    def NextPage(self):
        if self.CanNextPage():
            return self.jsonData(page=self.currPage+1)
        return '{}'

    def recordsInPage(self,page):
        total = 0
        for rec in page:
            total += len(rec.data)
        return total

    def SearchText(self,text):
        currentPage = None
        maxPerPage = 50
        filesInPage = 0
        buffer = io.StringIO()
        count = 0
        addText = ""
        for fn in EnumerateDir('./data'):
            fpn = False
            currentFile=None
            pp = hs.HtmlScanResult()
            pp.initScan()
            with open(fn,'rt') as input_file:
                pp.feed(input_file.read())
            pp.FlushLine()

            vq = query.QueryToken()
            vq.Reset()
            vq.CompileQuery(text)

            #print(pp.Lines)
            for ta in pp.Lines:
                vq.Reset()
                result = SearchInPara(ta['line'], vq, "<b>", "</b>")
                if result!=None:
                    if currentFile==None:
                        currentFile=CurrentSearchFileClass(fn,pp.Title)
                        #currentFile.data.append(currentFile)
                    currentFile.add({'text':result, 'tag':ta['tag'], 'num':ta['num']})
            #print('UI==>', currentFile.data)
            #print(currentFile)
            if currentFile!=None:
                #print('a')
                if currentPage==None:
                    #print('b')
                    currentPage=[]
                    self.pages.append(currentPage)
                    #print(self.pages, self.pages[0])
                #print('c')
                currentPage.append(currentFile)
                if self.recordsInPage(currentPage)>=maxPerPage:
                    currentPage=None
                currentFile=None
        #print(self.pages)

    def pageCount(self):
        return len(self.pages)

    def html(self,page=0):
        if len(self.pages)==0:
            return "<b>No Results</b>"
        self.currPage = page
        buffer = io.StringIO()
        buffer.write("<b>Page {}/{} Results</b>".format(page+1, len(self.pages)))
        buffer.write("<hr>")
        for file in self.pages[page]:
            file.writeTo(buffer)
        return buffer.getvalue()

    def jsonData(self,page=0):
        if len(self.pages)==0:
            return json.dumps({ 'currentPage': -1, 'pages': 0, 'canGoBack': False,
                'canGoForward': False, 'texts': [], 'query': self.query})
        self.currPage = page
        buffer = { 'currentPage': page+1,
            'pages': len(self.pages),
            'canGoBack': self.CanPrevPage(),
            'canGoForward': self.CanNextPage(),
            'query': self.query
        }
        texts = []
        for file in self.pages[page]:
            fr = {
                'title': file.title,
                'file': file.fileName,
                'text': file.data
            }
            texts.append(fr)
        buffer['texts'] = texts
        return json.dumps(buffer)

SearchHistory = SearchHistoryClass()


if __name__ == '__main__':
    #EnumerateDir("./data")
    #PrintWordLines("./data/index.html")

    # TODO: analyse query string
    # TODO: compare algorithm
    # TODO: reformatter for html file
    tst = ["this, is a query", "how can (I help you),(want this)"]
    for s in tst:
        vq = query.QueryToken()
        vq.CompileQuery(s)
        print("Query: ", s)
        vq.Print(1)

    vq = query.QueryToken()
    vq.Reset()
    vq.CompileQuery("\"this is text\"")
    ta = [ "we", "text", "want", "to", "see", "This", "is", "texts", "like", "this", "is", "texts", "this", "this", "is", "texts" ]
    print(SearchInPara(ta,vq,'<b>','</b>'))




    result = SearchHistory.Search("Gayatri MATA")
    print(result)
