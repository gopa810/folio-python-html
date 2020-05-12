import unicodedata as ucd

#long long compute_hash(string const& s) {
#    const int p = 31;
#    const int m = 1e9 + 9;
#    long long hash_value = 0;
#    long long p_pow = 1;
#    for (char c : s) {
#        hash_value = (hash_value + (c - 'a' + 1) * p_pow) % m;
#        p_pow = (p_pow * p) % m;
#    }
#    return hash_value;
#}

def to_oem(a):
    dc = ucd.decomposition(a)
    nc=' '
    if len(dc)>0:
        if dc.startswith('<compat>'):
            dc = dc[8:].lstrip()
        #print(dc, '--1')
        dc=dc[:dc.find(' ')]
        #print(dc, '--2')
        nc = chr(int(dc,16)).lower()
    else:
        nc = a.lower()
    #print(nc)
    return nc

def convert2oem(word):
    output = ''
    for a in word:
        output += to_oem(a)
    return output

def word2hash(word):
    p = 31
    m = 1000000009
    hash_value = 0
    p_pow = 1
    for a in word:
        nc = to_oem(a)
        hash_value = (hash_value + (ord(nc)-96)*p_pow ) % m
        p_pow = (p_pow * p) % m
    return hash_value

def compare_oem(s1,s2):
    if len(s1)!=len(s2):
        return False
    #print('===', s1, s2)
    for i in range(len(s1)):
        if to_oem(s1[i])!=to_oem(s2[i]):
            return False
    return True
