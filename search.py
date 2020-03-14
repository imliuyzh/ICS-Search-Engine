from nltk import PorterStemmer
import pickle
import time
import os
import math
import webbrowser
from itertools import islice
from urllib.parse import urlparse
from collections import defaultdict
import PySimpleGUI as sg

def get_total_tokens(): #sum = 413145
    sum = 0
    for f in "0123456789abcdefghijklmnopqrstuvwxyz":
        sum += len(pickle.load(open("./index/{}.p".format(f), 'rb')))
    return sum

n = 413145
idmap = pickle.load(open("idMap.p", 'rb'))
ps = PorterStemmer()
stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]

term_indices = pickle.load(open("file_indices_2.p", 'rb'))

class cache:
    store = []
    store_dict = {}

    @classmethod
    def get_index(cls, token):
        if token[0] in cache.store:
            return cache.store_dict[token[0]]
        else:
            cache.store.append(token[0])
            cache.store_dict[token[0]] = open("index3/{}.txt".format(token[0]), 'r')

            if len(cache.store) > 10:
                to_remove = cache.store.pop(0)
                del cache.store_dict[to_remove]

            return cache.store_dict[token[0]]

    @classmethod
    def clear(cls):
        cache.store = []
        cache.store_dict = {}

def get_token_info(token: str) -> dict: # {term: {docID: (important, count)}
    return cache.get_index(token)

#def get_token_info(token: str) -> dict: # {term: {docID: (important, count)}
#    p = pickle.load(open("./index/{}.p".format(token[0]), 'rb'))
#    return p[ps.stem(token)]

def get_term_info_dict_version(term: str) -> dict:
    with open("./index/{}.p".format(term[0]), 'rb') as p:
        index_dict = pickle.load(p)
        return index_dict[term]

def get_term_info_file_version(term: str) -> dict:
    term_info_file = cache.get_index(term)
    term_info_file.seek(term_indices[term])
    term_info = term_info_file.readline()
    term_info_list = term_info.split(',')
    term_info = {}
    for i in range(1, (len(term_info_list) - 4), 3):
        term_info[int(term_info_list[i])] = (bool(term_info_list[i+1]), int(term_info_list[i+2]))
    return term_info



def search(userIn: str) -> [int]:
    tokens = set(ps.stem(token) for token in (i for i in userIn.lower().split() if i not in stop_words))
    postings = get_tf_idf_list(tokens, list(ps.stem(token) for token in (i for i in userIn.lower().split() if i not in stop_words)))
    return postings

def getUrls(docIDs: frozenset) -> [str]:
    return [idmap[docid] for docid in docIDs]

def get_tf_idf_list(terms: set, userIn: [str]) -> [int]:
    term_dict = dict()
    for term in terms:
        term_dict[term] = get_term_info_file_version(term)
        #term_dict[term] = get_token_info(term)

    def find_document(doc_ids: set) -> dict:
        document_dict = {doc_id:dict() for doc_id in doc_ids}
        for doc_id in doc_ids:
            for term in terms:
                if doc_id not in term_dict[term].keys() and doc_id in document_dict:
                    document_dict.pop(doc_id)
        return document_dict

    doc_set = set()
    for term in terms:
        for doc_id in term_dict[term].keys():
            doc_set.add(doc_id)

    doc_vector_dict, query_vector_dict = find_document(doc_set), defaultdict(int)
    for docid in doc_vector_dict:
        for term in terms:
            tf, idf = (term_dict[term][docid][1] / idmap[docid][1]), (math.log(n / len(term_dict[term].keys())))
            doc_vector_dict[docid][term] = ((tf * idf * 1.5) if term_dict[term][docid][0] else (tf * idf))
            
    for term in terms:
        userInLen = len(userIn)
        tf, idf = (userIn.count(term) / userInLen), math.log(userInLen)
        query_vector_dict[term] = tf * idf
        
    for docid in doc_vector_dict:
        valueSum = 0
        for value in doc_vector_dict[docid].values():
            valueSum += (value**2)
        valueSum = math.sqrt(valueSum)
        for term in doc_vector_dict[docid]:
            doc_vector_dict[docid][term] /= valueSum
            
    result = 0
    for docid in doc_vector_dict:
        for term in doc_vector_dict[docid]:
            doc_vector_dict[docid][term] *= query_vector_dict[term]
            
    return sorted(doc_vector_dict, key=lambda x: -sum(doc_vector_dict[x].values()))

# index = {term: {docID: (important, count)}}
# idMap = {id_int: (url, terms_in_document)}

def getNextUrl(results: [int], numResults=5) -> str:   #idmap[e[counter][0]][0]
    resultLen = len(results)
    pageCt = 0
    triedPages = 0
    visited = set()
    #print(results)
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
    # print("End of results")

def define_layout():
    return [
        [sg.Text(text="Please enter a query:", text_color="black", pad=((10,0),(10,0)), font=("Segoe UI", 17), background_color="white", key="prompt_text")],
        [sg.InputText(default_text="", pad=((10,10),(10,10)), key="search_box"), sg.Button(button_text="Submit", font=("Segoe UI", 12), size=(15,1), pad=((0,0),(7,7)), button_color=("black","white"), disabled=False, border_width=2, key="search_button")]
    ]

if __name__ == "__main__":
    layout = define_layout()
    window = sg.Window(title="Index Search", element_justification="left", margins=(5,5), background_color="white").Layout(layout)
    while True:
        event, values = window.read()
        if event in (None, "exit"):
            break
        if event is not None:
            t = time.time()
            searchResults = search(values["search_box"])
            t = time.time() - t
            print('The query: {0} took {1} seconds to run'.format(values["search_box"], t))
            results_list = [page for page in getNextUrl(searchResults)]
            if len(results_list) == 0:
                results_list = ["No results were found"]
            results_layout = [[sg.Text(text=results_text, text_color="blue", pad=((15,15),(10,0)), font=("Segoe UI", 12), relief="ridge", background_color="white", key=results_text, enable_events=True)] for results_text in results_list]
            results_window = sg.Window(title="Search Thing", element_justification="left", margins=(5,15), background_color="white").Layout(results_layout)
            while True:
                results_event, results_values = results_window.read()
                if results_event in (None, "exit"):
                    break
                if results_event in results_list and results_list[0] is not "No results were found":
                    webbrowser.open(url=results_event, new=1)
            results_window.close()
            cache.clear()
    window.close()


    # inp = input("Please enter a query (or enter :q to exit): ")
    # while inp != ":q":
    #     t = time.time()
    #     searchResults = search(inp)
    #     t = time.time() - t
    #     for page in getNextUrl(searchResults):
    #         print(page)
    #     print("Your query took {} seconds.\n".format(t))
    #     inp = input("Please enter a query (or enter :q to exit): ")
    #     cache.clear()