from nltk import PorterStemmer
import pickle
import time
import os
import math
from itertools import islice
from urllib.parse import urlparse

def get_total_tokens():
    sum = 0
    for f in "0123456789abcdefghijklmnopqrstuvwxyz":
        sum += len(pickle.load(open("./index/{}.p".format(f), 'rb')))
    return sum

n = get_total_tokens()
idmap = pickle.load(open("idMap.p", 'rb'))
stops = pickle.load(open("stops.p", 'rb'))
ps = PorterStemmer()
term_freqs = dict()
id_freqs = dict()
stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

term_indices = {} #pickle.load(open("term_indices.p", 'rb'))
ORIGINAL = 0
DICT = 1
FILE = 2

MODE = ORIGINAL

class cache:
    store = []
    store_dict = {}

    @classmethod
    def get_index(cls, token):
        if token[0] in cache.store:
            return cache.store_dict[token[0]][ps.stem(token)]
        else:
            p = pickle.load(open("./index/{}.p".format(token[0]), 'rb'))
            cache.store.append(token[0])
            cache.store_dict[token[0]] = p

            if len(cache.store) > 3:
                to_remove = cache.store.pop(0)
                del cache.store_dict[to_remove]

            return p[ps.stem(token)]

def get_token_info(token: str) -> dict: # {term: {docID: (important, count)}
    return cache.get_index(token)

def search(userIn: str) -> [int]:
    tokens = set(ps.stem(token) for token in (i for i in userIn.lower().split() if i not in stop_words))
    postings = get_tf_idf_list(tokens) 
    return postings

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]

def get_tf_idf_list(terms: set) -> [int]:

    term_dict = dict()
    for term in terms:
        term_dict[term] = get_token_info(term)

    def find_document(doc_ids: set) -> dict:
        document_dict = {doc_id:0 for doc_id in doc_ids}
        for doc_id in doc_ids:
            for term in terms:
                if doc_id not in term_dict[term].keys():
                    try:
                        document_dict.pop(doc_id)
                    except:
                        pass
        return document_dict

    doc_set = set()
    for term in terms:
        for doc_id in term_dict[term].keys():
            doc_set.add(doc_id)

    tf_idf_dict = find_document(doc_set)
    for docid in tf_idf_dict:
        for term in terms:
            tf, idf = (term_dict[term][docid][1] / idmap[docid][1]), (math.log(n / len(term_dict[term].keys())))
            tf_idf_dict[docid] += (tf * idf)
    return sorted(tf_idf_dict, key=lambda x: -tf_idf_dict[x])

# index = {term: {docID: (important, count)}}
# idMap = {id_int: (url, terms_in_document)}

def getNextUrl(results: list, numResults=5) -> str:   #idmap[e[counter][0]][0]
    resultLen = len(results)
    pageCt = 0
    triedPages = 0
    visited = set()
    print(results)
    while pageCt < numResults and triedPages < resultLen:
        url = idmap[results[triedPages]][0]
        parsedUrl = urlparse(url)
        pathMinusFile = tuple(parsedUrl.path[1:].split('/')[:-1])
        if not parsedUrl.path:
            pageCt += 1
            yield url

        elif pathMinusFile not in visited:
            visited.add(pathMinusFile)
            pageCt += 1
            yield url
        triedPages += 1
    print("End of results")



if __name__ == "__main__":
    inp = input("Please enter a query (or enter :q to exit): ")
    while inp != ":q":
        t = time.time()
        searchResults = search(inp)
        t = time.time() - t
        for page in getNextUrl(searchResults):
            print(page)
        print("Your query took {} seconds.\n".format(t))
        inp = input("Please enter a query (or enter :q to exit): ")
