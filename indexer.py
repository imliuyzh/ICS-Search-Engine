import json, re, pickle, datetime
from collections import defaultdict
from os.path import isfile, join
from os import walk
from bs4 import BeautifulSoup
from nltk import PorterStemmer
from sys import getsizeof

tokenMatch = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> [str]:
    """Take a string and break it down to a list of alphanumeric sequences."""
    return re.findall(tokenMatch, text.lower())


def removeNoise(documentTree: BeautifulSoup) -> None:
    """Clear all the data noise from the given document tree."""
    for x in documentTree.findAll(["script", "style", "head"]):
        x.extract()


def parse(toParse: dict) -> ([str], [str]):
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
    old = pickle.load(open("index.p", "rb"))
    for key, ids in new.items():
        old[key] = old[key].union(ids)
    pickle.dump(old, open("index.p", "wb"))
    new.clear()


def index() -> None:
    n = 0  # docid
    i = defaultdict(set)  # tokens
    pickle.dump(i, open("index.p", "wb"))
    ps = PorterStemmer()
    idMap = defaultdict(str)

    # start time
    print("start time: {0}".format(datetime.datetime.now()))

    # From Stack Overflow

    for indexerPath, _, files in walk("./DEV", topdown=False):
        for file_name in files:
            with open(join(indexerPath, file_name)) as jsonFile:
                n = n + 1
                jFile = json.load(jsonFile)
                idMap[n] = jFile['url']
                importantTokens, normalTokens = parse(jFile)
                for token in importantTokens:
                    i[ps.stem(token)].add(n)
                for token in normalTokens:
                    if token.isalpha():  # or not token.isnumeric()
                        i[ps.stem(token)].add(n)

                if getsizeof(i) > 10000000:
                    writeToIndex(i)

    writeToIndex(i)
    pickle.dump(idMap, open("idMap.p", 'wb'))

    i = pickle.load(open("index.p", "rb"))

    print("{0} unique documents".format(n))
    print("{0} unique tokens".format(len(i.keys())))

    # end time
    print("end time: {0}".format(datetime.datetime.now()))


if __name__ == '__main__':
    index()
