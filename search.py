from nltk import PorterStemmer
import pickle
import time
import math
from itertools import islice

index = pickle.load(open("index.p", 'rb' ))
n = len(index)
idmap = pickle.load(open("idMap.p", 'rb'))
stops = pickle.load(open("stops.p", 'rb'))
ps = PorterStemmer()
term_freqs = dict()
id_freqs = dict()
def search(userIn: str) -> [str]:
    stemmed = set(ps.stem(token) for token in userIn.lower().split())
    return get_tf_idf_list(stemmed)

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]


def get_tf_idf_list(term):

    def tf(term, docid):
        return index[term][docid][1] / idmap[docid][1]

    def idf(term):
        return math.log(n / len(index[term].keys()))

    def tf_idf(term, docid):
        return tf(term, docid) * idf(term)

    tf_idf_list = []
    for docid in index[term].keys():
        print(docid)
        tf_idf_list.append((docid, tf_idf(term, docid)))

    return sorted(tf_idf_list, key=lambda x: x[1])

# index  = {term: {docID: (important, count) } }
# idMap = { id_int : ( url, terms_in_document )  }

if __name__ == "__main__":
    inp = ''
    print("Please enter a query (or enter :q to exit)")
    inp = input()

    print(get_tf_idf_list(inp))
    while inp != ":q":
        t = time.time()
        e = search(inp)
        t = time.time() - t
        print(e, t, len(e))
        print("Please enter a query: ")
        inp = input()

