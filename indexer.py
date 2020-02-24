import json, re, pickle
from collections import defaultdict
from os import listdir
from os.path import isfile, join
from os import walk
from bs4 import BeautifulSoup
from nltk import PorterStemmer
import datetime
from sys import getsizeof

#implement
def tokenize(text: str) -> [str]:
    """Take a string and break it down to a list of alphanumeric sequences."""
    return re.findall(r"[a-z0-9]+", text.lower())

def removeNoise(documentTree: BeautifulSoup) -> None:
    """Clear all the data noise from the given document tree."""
    for x in documentTree.findAll(["script", "style", "head"]):
        x.extract()

def parse(toParse: dict) -> ([str], [str]):
    """Given a JSON dict and parse it into lists of tokens."""
    soup = BeautifulSoup(toParse['content'], 'lxml')
    
    importantCandidate = soup.findAll(["title", "strong", "b", "h1",
        "h2", "h3", "h4", "h5", "h6"])
    importantToken = []
    for x in importantCandidate:
        importantToken.extend(tokenize(x.extract().get_text()))
    
    removeNoise(soup)
    normalToken = tokenize(soup.get_text())
    return importantToken, normalToken

def writeToIndex(new):
    """Dumps >10MB index to old index"""
    old = pickle.load(open("index.p", "rb"))
    for key, set in new.items():
        old[key] = old[key].union(set)
    pickle.dump(old, open("index.p", "wb"))
    new.clear()

def index():
    n = 0 # docid
    i = defaultdict(set) #tokens
    pickle.dump(i, open("index.p", "wb"))
    ps = PorterStemmer()

    #start time
    print("start time: {0}".format(datetime.datetime.now()))

    # From Stack Overflow
    # below line has old small documents option
    #for file_name in [f for f in listdir("./documents") if isfile(join("./documents", f))]:
    for dirpath, _, files in walk("./documents", topdown=False):
        for file_name in files:
            with open(join(dirpath, file_name)) as jsonFile:
                n = n + 1
                importantToken, normalToken = parse(json.load(jsonFile))
                for token in importantToken + normalToken:
                    i[ps.stem(token)].add(n)
                if getsizeof(i) > 10000000:
                    writeToIndex(i)

    writeToIndex(i)

    i = pickle.load(open("index.p", "rb"))

    print("{0} unique documents".format(n))
    print("{0} unique tokens".format(len(i.keys())))

    #end time
    print("end time: {0}".format(datetime.datetime.now()))

if __name__ == '__main__':
    index()
