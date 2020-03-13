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

term_indices = {} #pickle.load(open("term_indices.p", 'rb'))
ORIGINAL = 0
DICT = 1
FILE = 2

MODE = ORIGINAL


def get_token_info(token: str) -> dict: # {term: {docID: (important, count)}
    p = pickle.load(open("./index/{}.p".format(token[0]), 'rb'))
    return p[ps.stem(token)]

def get_term_info_dict_version(term: str) -> dict:
    with open("./index/{}.p".format(term[0]), 'rb') as p:
        index_dict = pickle.load(p)
        return index_dict[term]

def get_term_info_file_version(term: str, open_index_files: dict) -> dict:
    term_info_file = open_index_files[term[0]]
    term_info_file.seek(term_indices[term])
    term_info = term_info_file.readline()
    term_info_list = term_info.split(',')
    term_info = {}
    for i in range(1, (len(term_info_list) - 3)):
        term_info[term_info_list[i]] = (term_info_list[i+1], term_info_list[i+2])
    return term_info



def search(userIn: str) -> [int]:
    tokens = set(ps.stem(token) for token in userIn.lower().split())
    postings = get_tf_idf_list(tokens) 
    return postings

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]

def get_tf_idf_list(terms: set) -> [int]:

    term_dict = dict()
    for term in terms:
        term_dict[term] = get_term_info_dict_version(term)

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
