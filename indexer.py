import json
from collections import defaultdict
import os
import re
from bs4 import BeautifulSoup


#implement
def parse(toParse : str) -> [str]:
    htmlStr = json.loads(toParse)['content']
    soup = BeautifulSoup(htmlStr, 'lxml')
    [x.extract() for x in soup.findAll('script')]
    [x.extract() for x in soup.findAll('style')]

    def tokenize(text: str) -> list:
        return re.sub(r'[^a-z0-9]', " ", text.lower()).split()

    return tokenize(soup.text)

def index():
    n = 0 # docid
    i = defaultdict(set) #tokens

    #test parser
    print(os.getcwd())
    f = open(os.getcwd() + '\\documents\\086a1bfe6d5fc2a3b99b497026bbb79825e72ef608c9f34b03fa0ef480d5c2be.json')
    for line in f:
        print(parse(line))

if __name__ == '__main__':
    index()