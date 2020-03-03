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


def search(userIn: str) -> [int]:
    tokens = set(ps.stem(token) for token in userIn.lower().split())
    postings = get_tf_idf_list(tokens) 
    return postings[0:5]

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]

def get_tf_idf_list(terms: set) -> [int]:
    def find_document(doc_ids: set) -> dict:
        document_dict = {doc_id:0 for doc_id in doc_ids}
        for doc_id in doc_ids:
            for term in terms:
                if doc_id not in index[term].keys():
                    try:
                        document_dict.pop(doc_id)
                    except:
                        pass
        return document_dict
    
    doc_set = set()
    for term in terms:
        for doc_id in index[term].keys():
            doc_set.add(doc_id)

    tf_idf_dict = find_document(doc_set)
    for docid in tf_idf_dict:
        for term in terms:
            tf, idf = (index[term][docid][1] / idmap[docid][1]), (math.log(n / len(index[term].keys())))
            tf_idf_dict[docid] += (tf * idf)
    return sorted(tf_idf_dict, key=lambda x: -tf_idf_dict[x])

# index = {term: {docID: (important, count)}}
# idMap = {id_int: (url, terms_in_document)}

if __name__ == "__main__":
    inp = input("Please enter a query (or enter :q to exit): ")
    while inp != ":q":
        t = time.time()
        e = search(inp)
        t = time.time() - t
        print(e, t, len(e))
        for doc in e:
            print(idmap[doc][0])
        inp = input("Please enter a query: ")
