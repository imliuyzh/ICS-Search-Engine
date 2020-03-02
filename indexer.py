import json, re, pickle, datetime, time
from collections import defaultdict
from os.path import isfile, join
from os import walk
from bs4 import BeautifulSoup
from nltk import PorterStemmer
from sys import getsizeof
from urllib.parse import urlparse

tokenMatch = re.compile(r"[a-z0-9]+")
ps = PorterStemmer()

def tokenize(text: str) -> [str]:
    """Take a string and break it down to a list of alphanumeric sequences, and stems."""
    return list( ps.stem(token) for token in re.findall(tokenMatch, text.lower()) )


def removeNoise(documentTree: BeautifulSoup) -> None:
    """Clear all the data noise from the given document tree."""
    for x in documentTree.findAll(["script", "style", "head"]):
        x.extract()


def parseTokens(toParse: dict) -> ([str], [str]):
    """Given a JSON dict and parse it into lists of tokens."""
    soup = BeautifulSoup(toParse['content'], 'lxml')

    importantCandidate = soup.findAll(["title", "strong", "b", "h1",
                                       "h2", "h3", "h4", "h5", "h6"])
    importantTokens = []
    for x in importantCandidate:
        importantTokens.extend(tokenize(x.extract().get_text()))

    removeNoise(soup)
    normalTokens = tokenize(soup.get_text())
    return importantTokens, normalTokens


def writeToIndex(new: dict) -> None:
    """Dumps >10MB index to old index"""
    print('Dumping dictionary.', end='')
    old = pickle.load(open("index.p", "rb"))
    print('.', end='')
    for key, docDict in new.items():
        for docID, info in docDict.items():
            old[key][docID] = info
    print('.', end='')
    pickle.dump(old, open("index.p", "wb"))
    print(' Done.')
    new.clear()


def tokenCounter(imp, norm) -> dict:
    '''sum contents of parseTokens return'''
    countDict = defaultdict(int)
    out = set()
    for token in imp + norm:
        countDict[token] += 1

    return countDict


def index() -> None:
    n = 0  # docid
    i = defaultdict(dict)  # index  = {term: {docID: (important, count) } }
    pickle.dump(i, open("index.p", "wb"))
    visitedUrls = set()
    skipped = 0
    idMap = dict()  # idMap = { id_int : ( url, terms_in_document )  }

    # start time
    print("start time: {0}".format(datetime.datetime.now()))
    # From Stack Overflow
    t = time.time()
    for indexerPath, _, files in walk("./DEV", topdown=True):
        for file_name in files:
            with open(join(indexerPath, file_name)) as jsonFile:
                jFile = json.load(jsonFile)
                pjFile = urlparse(jFile['url'])[1:4]
                if pjFile in visitedUrls:
                    skipped += 1
                else:
                    visitedUrls.add(pjFile)
                    n += 1
                    importantTokens, normalTokens = parseTokens(jFile)
                    tokenCounts = tokenCounter(importantTokens, normalTokens)

                    for token in normalTokens:
                        if not token.isnumeric():
                            i[token][n] = (False, tokenCounts[token])
                    for token in importantTokens:
                        i[token][n] = (True, tokenCounts[token])
                    idMap[n] = (jFile['url'], len(importantTokens) + len(normalTokens))
                    if getsizeof(i) > 10000000:
                        writeToIndex(i)

                    if n % 50 == 0:
                        print("docID: {0} of 50k, {1} skipped ({2:.4f}%), t+{3:.1f}s".format(n, skipped,
                                                                                            skipped / (n + skipped),
                                                                                            time.time() - t)
                              )

    writeToIndex(i)
    pickle.dump(idMap, open("idMap.p", 'wb'))
    i = pickle.load(open("index.p", "rb"))

    print("{0} unique documents".format(n))
    print("{0} unique tokens".format(len(i.keys())))

    # end time
    print("end time: {0}".format(datetime.datetime.now()))


if __name__ == '__main__':
    index()
