import json, os, re
from collections import defaultdict
from bs4 import BeautifulSoup


#implement
def tokenize(text: str) -> [str]:
    """Take a string and break it down to a list of alphanumeric sequences."""
    return re.findall(r"[a-z0-9]+", text.lower())
    #return re.sub(r'[^a-z0-9]', " ", text.lower()).split()

def removeNoise(documentTree: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
    """Clear all the data noise from the webpage given."""
    for x in documentTree.findAll(["script", "style", "head"]):
        x.extract()
    return documentTree

def parse(toParse: str) -> ([str], [str]):
    """Given a HTML string and parse it into a list of tokens."""
    soup = BeautifulSoup(json.loads(toParse)['content'], 'lxml')
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

    #test parser
    print(os.getcwd())
    f = open(os.getcwd() + '\\documents\\086a1bfe6d5fc2a3b99b497026bbb79825e72ef608c9f34b03fa0ef480d5c2be.json')
    for line in f:
        print(parse(line))
    f.close()

if __name__ == '__main__':
    index()
