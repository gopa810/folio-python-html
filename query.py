# system
import re
import unicodedata as ucd

# local
import conv

HLNone = 0
HLNormal = 1
HLBold = 2

AT_Sys     = 0
AT_Text    = 1
AT_Regexp  = 2
AT_Group   = 3
AT_Phrase  = 4
AT_Or      = 5

QueryTextScopeLen = 5

def NewTextAtom(s):
    qa = QueryToken()
    qa.Type = AT_Text
    qa.Text = s
    return qa

def NewSysAtom(s):
    qa = QueryToken()
    qa.Type = AT_Sys
    qa.Text = s
    return qa

def IsTokenChar(q):
    cat = ucd.category(q)
    return cat=='Ll' or cat=='Lu' or cat=='Nd' or q == '?' or q== '*' or q=='-' or q=='_'


class QueryToken:
    def __init__(self,rangeLen=QueryTextScopeLen):
        self.Type = None
        self.Text = ''
        self.Rx = None
        self.Group = None
        self.Position = -1
        self.Positions = []
        self.QueryScopeRange = rangeLen


    def AddPos(qt,pos):
        if qt.Positions == None:
            qt.Positions = []
        if len(qt.Positions)==0 or qt.Positions[-1] != pos:
            qt.Position = pos
        qt.Positions.append(pos)

    def ClearPos(qt):
        qt.Position = -1

    def Projection(qt,pa):
      lpa = len(pa)
      for p in qt.Positions:
          for i2 in range(p-qt.QueryScopeRange,p+qt.QueryScopeRange,1):
              if i2 >= 0 and i2 < lpa and pa[i2] == HLNone:
                  pa[i2] = HLNormal
          pa[p] = HLBold
      if qt.Group != None:
          for p in qt.Group:
              p.Projection(pa)

    def Reset(qt):
      qt.Position = -1
      qt.Positions = []
      if qt.Group != None:
          for p in qt.Group:
              p.Reset()

    def Match(qt,s,pos):
        if qt.Type == AT_Text:
            if conv.compare_oem(qt.Text,s):
                qt.AddPos(pos)
                return 1
        elif qt.Type == AT_Regexp:
            if qt.Rx == None:
                qt.Rx = re.compile(qt.Text)
            if qt.Rx.match(s):
                qt.AddPos(pos)
                return 1
        elif qt.Type == AT_Group:
            c = 0
            matched = False
            for p in qt.Group:
                if p.Match(s,pos) > 0:
                    matched = True
                #print('p.position:', p.Position)
                if p.Position >= 0:
                    c+=1
            if c == len(qt.Group) and matched:
                qt.AddPos(pos)
                return 1
            qt.Position = -1
            return 0
        elif qt.Type == AT_Phrase:
            c = 0
            matched = False
            for j,p in enumerate(qt.Group):
                if p.Match(s,pos) > 0:
                    matched = True
                    for j2 in range(len(qt.Group)):
                        if j2 > j:
                            qt.Group[j2].ClearPos()
                if p.Position > 0:
                    c+=1
            if not matched:
                c = -1
            if c == len(qt.Group):
                c = 0
                for i,p in enumerate(qt.Group):
                    if i == 0 and p.Position >= 0:
                        c+=1
                    elif i > 0 and p.Position >= 0 and p.Position <= qt.Group[i-1].Position + 2:
                        c+=1
            if c == len(qt.Group):
                qt.AddPos(pos)
                return 1
            qt.Position = -1
            return 0
        return 0

    def Print(qt,level):
        for j in range(level):
            print(" ", end='')
        print("+ {} {} [ ".format(qt.Type, qt.Text), end='')
        if qt.Positions != None:
            for pi in qt.Positions:
                print("{} ".format(pi),end='')
        print(']')

        if qt.Group != None:
            for q in qt.Group:
                q.Print(level + 2)


    def GetPhraseInterval(qt):
        A = -1
        B = -1
        if qt.Group == None:
            return -1,-1
        for i,q in enumerate(qt.Group):
            if q.Text == "\"" and q.Type == AT_Sys:
                if A < 0:
                    A = i
                else:
                    B = i
                    break
        return A,B

    def Add(qt,q):
        qt.Group.append(q)

    def GetGroupInterval(qt):
        A = -1
        B = -1
        if qt.Group != None:
            for i,q in enumerate(qt.Group):
                if q.Text == "(" and q.Type == AT_Sys:
                    A = i
                if q.Text == ")" and q.Type == AT_Sys:
                    B = i
                    break
        return A,B

    def GetOrInterval(qt):
        A = -1
        if qt.Group != None:
            for i,q in enumerate(qt.Group):
                if q.Text == "," and q.Type == AT_Sys:
                    A = i
                    break
        return A

    def ReduceOr(qt):
        a = -1
        for p in qt.Group:
            if p.Type == AT_Group or p.Type == AT_Phrase:
                p.ReduceOr()
        a = qt.GetOrInterval()
        while a > 0:
            if a >= len(qt.Group)-1:
              break
            group = QueryToken()
            group.Type = AT_Or
            group.Group = [qt.Group[a-1],qt.Group[a+1]]
            a1 = qt.Group[:a-1]
            a2 = qt.Group[a+2:]
            qt.Group = a1
            qt.Group.append(group)
            qt.Group += a2
            a = qt.GetOrInterval()
        return

    def CompileQuery(this,query):
        mode = 0
        query += " "
        this.Group = []
        this.Type = AT_Group
        this.Text = ""
        # split text to atoms
        for q in query:
            if IsTokenChar(q):
                this.Text += str(q)
            else:
                if len(this.Text)>0:
                    this.Add(NewTextAtom(this.Text))
                    this.Text = ''
