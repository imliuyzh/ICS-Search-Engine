import json, re
from collections import defaultdict
from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
import pickle
from nltk import PorterStemmer

#implement
def tokenize(text: str) -> [str]:
    """Take a string and break it down to a list of alphanumeric sequences."""
    return re.findall(r"[a-z0-9]+", text.lower())
    #return re.sub(r'[^a-z0-9]', " ", text.lower()).split()

def removeNoise(documentTree: BeautifulSoup) -> None:
    """Clear all the data noise from the given document tree."""
    for x in documentTree.findAll(["script", "style", "head"]):
        x.extract()

def parse(toParse: dict) -> ([str], [str]):
    """Given a HTML string and parse it into a list of tokens."""
    soup = BeautifulSoup(toParse['content'], 'lxml')
    importantToken = []
    for x in soup.findAll([
        "title", "strong", "b", "h1", "h2", "h3", "h4", "h5", "h6"]):
        importantToken.extend(tokenize(x.extract().get_text()))
    removeNoise(soup)
    normalToken = tokenize(soup.get_text())
    return importantToken, normalToken

def index():
    n = 0 # docid
    i = defaultdict(set) #tokens
    ps = PorterStemmer()

    #the code for opening these files is from stack overflow
    for file_name in [f for f in listdir("./documents") if isfile(join("./documents", f))]:
        with open("./documents/" + file_name) as jsonFile:
            n = n + 1
            importantToken, normalToken = parse(json.load(jsonFile))
            for token in importantToken + normalToken:
                i[ps.stem(token)].add(n)

    print("{0} unique documents".format(n))
    print("{0} unique tokens".format(len(i.keys())))
    pickle.dump(i, open("index.p", "wb"))

if __name__ == '__main__':
    index()
