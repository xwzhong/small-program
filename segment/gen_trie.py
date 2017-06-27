# -*- coding: utf-8 -*-
"""
@author: xwzhong
"""

def gen_trie(f_name):  
    lfreq = {}  
    trie = {}  
    ltotal = 0.0  
    with open(f_name, 'rb') as f:  
        lineno = 0   
        for line in f.read().rstrip().decode('utf-8').split('\n'):  
            lineno += 1  
            try:  
                word,freq,_ = line.split(' ')  
                freq = float(freq)  
                lfreq[word] = freq  
                ltotal+=freq  
                p = trie  
                for c in word:  
                    if c not in p:  
                        p[c] ={}  
                    p = p[c]  
                p['']='' #ending flag  
            except ValueError, e:  
                logger.debug('%s at line %s %s' % (f_name,  lineno, line))  
                raise ValueError, e  
    return trie, lfreq, ltotal  
