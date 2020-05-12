
class RequestArguments:
    def __init__(self):
        self.p = []

    def SetString(R,s):
        p1 = s.split("/")
        R.p = []

        for v in p1:
            if len(v) > 0:
                R.p.append(v)

        print("Request: ", R.p)

    def Count(R):
        return len(R.p)

    def Arg(R,i):
        if i >= len(R.p):
            return ""
        return R.p[i]

    def GetString(R):
        return ','.join(R.p)
