from nltk import PorterStemmer
import pickle
import time
import math
from itertools import islice

index = pickle.load(open("index.p", 'rb'))
n = len(index)
idmap = pickle.load(open("idMap.p", 'rb'))
stops = pickle.load(open("stops.p", 'rb'))
ps = PorterStemmer()
term_freqs = dict()
id_freqs = dict()


def search(userIn: str) -> [str]:
    tokens = set(ps.stem(token) for token in userIn.lower().split())
    postings = []
    for token in tokens:
        token_posting = get_tf_idf_list(token)
        postings.extend(token_posting)
        print(token_posting)
    return postings

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]

def get_tf_idf_list(term):
    def tf_idf(term, docid):
        tf, idf = (index[term][docid][1] / idmap[docid][1]), (math.log(n / len(index[term].keys())))
        return tf * idf

    tf_idf_list = []
    for docid in index[term].keys():
        print(docid)
        tf_idf_list.append((docid, tf_idf(term, docid)))
        
    tf_idf_list.sort(key=lambda x: x[1])
    return tf_idf_list

# index  = {term: {docID: (important, count) } }
# idMap = { id_int : ( url, terms_in_document )  }

if __name__ == "__main__":
    inp = input("Please enter a query (or enter :q to exit): ")
    while inp != ":q":
        t = time.time()
        e = search(inp)
        t = time.time() - t
        print(e, t, len(e))
        inp = input("Please enter a query: ")

