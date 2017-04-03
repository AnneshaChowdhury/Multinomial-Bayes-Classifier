
from nltk.stem import SnowballStemmer 
import re
import sys
import os
import math

stemmer = SnowballStemmer("english")
regx = re.compile("[^a-zA-Z]")
subpaths = {"alt.atheism", "misc.forsale", "rec.autos", "sci.crypt", "talk.politics.guns"}

trainstat = {
    "alt.atheism": {},
    "misc.forsale": {},
    "rec.autos": {},
    "sci.crypt": {},
    "talk.politics.guns": {}
    }

percentage = {
    "alt.atheism": {},
    "misc.forsale": {},
    "rec.autos": {},
    "sci.crypt": {},
    "talk.politics.guns": {}
    }

alphabet = 0    
def ScanTrainLine(line, category):
    
    strings = regx.split(line)
    for str in strings:
        size = len(str)
        if size <= 2:  
            continue
        else:
            str = stemmer.stem(str)
            times = trainstat[category].get(str, 0);
            times = times + 1
            trainstat[category][str] = times


def ScanTrainFile(filename, category):
    filehandle = open(filename)
    filelines = filehandle.readlines()
    start = False
    for line in filelines:
        if not start:
            if line.startswith("lines:") or line.startswith("Lines:"):
                start = True
        else:
            ScanTrainLine(line, category)


def ScanTrainDir(dirpath):
    for path in subpaths: 
        trainpath = dirpath + "\\" + path + "\\"
        for fn in os.listdir(trainpath):
            fullname = trainpath + fn
            ScanTrainFile(fullname, path)

    
def CalcTrainStat():
    
    wordlist = {}
    wordsum = 0
    
    for key, stat in trainstat.items():
        sum = 0
        for token, count in stat.items():
            sum = sum + count
            wordlist[token] = 1
        stat[u'_num'] = sum     
        wordsum = wordsum + sum     

    alphabet = len(wordlist)  

    
    for key, stat in trainstat.items():
        stat[u'_percent'] = stat[u'_num'] * 1.0 / wordsum
        ratiomap = percentage[key]
        for token, count in stat.items():
            if token.startswith(u'_'):
                continue
            else:
                ratiomap[token] = (stat[token] + 1) * 1.0 / (stat[u'_num'] + alphabet)


def ScanTestLine(line, worddict):
     
    strings = regx.split(line)
    for str in strings:
        size = len(str)
        if size <= 1:
            continue
        else:
            str = stemmer.stem(str)
            times = worddict.get(str, 0);
            times = times + 1
            worddict[str] = times


def ScanTestFile(filename, category):
    filehandle = open(filename)
    filelines = filehandle.readlines()
    start = False
    worddict = {}    
    
    for line in filelines:
        if not start:
            if line.startswith("lines:") or line.startswith("Lines:"):
                start = True
        else:
            ScanTestLine(line, worddict)
    
    maxlog = -100000000.0
    maxcat = ""
    categorys = subpaths
    
    for cat in categorys: 
        tmplog = math.log(trainstat[cat][u'_percent'])
        for word, count in worddict.items():
            icount = 0
            wordappear = trainstat[cat].get(word, 0)
            logforword = 0
            if wordappear == 0:
                logforword = 1.0 / (trainstat[cat][u'_num'] + alphabet)
            else:
                logforword = percentage[cat][word]
            while icount < count:
                tmplog = tmplog + math.log(logforword)
                icount = icount + 1

        if tmplog > maxlog:
            maxlog = tmplog
            maxcat = cat
    
    if maxcat == category:
        return True
    else:
        return False

def ScanTestDir(dirpath):
    for path in subpaths: 
        testpath = dirpath + "\\" + path + "\\"
        filenum = 0
        rightnum = 0
        
        for fn in os.listdir(testpath):
            filenum = filenum + 1
            fullname = testpath + fn
            
            ret = ScanTestFile(fullname, path)
            if ret:
                rightnum = rightnum + 1
        print ("Testing class [" + path + "], the accuracy is: " + str(rightnum * 1.0 / filenum))

if len(sys.argv) != 3:
    print ("Usage: python MNB.py traindir testdir")
    sys.exit(0)

ScanTrainDir(sys.argv[1])
CalcTrainStat()
ScanTestDir(sys.argv[2])

