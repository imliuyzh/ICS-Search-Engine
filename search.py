from nltk import PorterStemmer
import pickle
import time
from itertools import islice

index = pickle.load(open("indexr1.p", 'rb' ))
idmap = pickle.load(open("idMap.p", 'rb'))

def search(userIn : str )->[str]:
    ps = PorterStemmer()

    inputTokens = userIn.split()
    if len(inputTokens) == 1:
        return index[ps.stem(userIn)]
    sets = set()
    for token in inputTokens:
        sets.add(frozenset(index[ps.stem(token)]))

    return getUrls(frozenset.intersection(*sets))

def getUrls(docIDs : set) -> [str]:

    return [idmap[url] for url in docIDs]


if __name__ == "__main__":
    print("Please enter a query")

    inp = input()
    t = time.time()
    e = search(inp)
    t = time.time() - t
    print(e, t)

