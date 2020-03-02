from nltk import PorterStemmer
import pickle
import time
from itertools import islice

index = pickle.load(open("indexr1.p", 'rb' ))
idmap = pickle.load(open("idMap.p", 'rb'))
stops = pickle.load(open("stops.p", 'rb'))

def search(userIn:str) -> [str]:
    ps = PorterStemmer()

    inputTokens = userIn.split()
    if len(inputTokens) == 1:
        return index[ps.stem(userIn)]
    sets = set()
    for token in inputTokens:
        if token not in stops:
            sets.add(frozenset(index[ps.stem(token)]))

    return getUrls(frozenset.intersection(*sets))

def getUrls(docIDs : set) -> [str]:

    return [idmap[id] for id in docIDs]


if __name__ == "__main__":
    inp = ''
    print("Please enter a query (or enter :q to exit)")
    inp = input()
    while inp != ":q":
        t = time.time()
        e = search(inp)
        t = time.time() - t
        print(e, t, len(e))
        print("Please enter a query")
        inp = input()

