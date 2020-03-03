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
    postings = get_tf_idf_list(tokens) 
    print(posting)
    return postings

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]

def get_tf_idf_list(terms: set) -> [(int, int)]:
    def find_document(doc_ids: set) -> dict:
        document_dict = {doc_id:0 for doc_id in doc_ids}
        for doc_id in doc_ids:
            for term in terms:
                if doc_id not in index[term].keys():
                    document_dict.pop(doc_id)
        return document_dict
        
    tf_idf_dict = find_document(set(doc_id for doc_id in index[term].keys() for term in terms))
    for docid in tf_idf_dict:
        for term in terms:
            tf, idf = (index[term][docid][1] / idmap[docid][1]), (math.log(n / len(index[term].keys())))
            tf_idf_dict[docid] += (tf * idf)
    return sorted(tf_idf_dict, key=lambda x: x[1])

# index = {term: {docID: (important, count)}}
# idMap = {id_int: (url, terms_in_document)}

if __name__ == "__main__":
    inp = input("Please enter a query (or enter :q to exit): ")
    while inp != ":q":
        t = time.time()
        e = search(inp)
        t = time.time() - t
        print(e, t, len(e))
        for counter in range(0, 5):
            print(idmap[e[counter][0]][0])
        inp = input("Please enter a query: ")
