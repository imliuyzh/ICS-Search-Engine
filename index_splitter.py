import pickle
from string import ascii_lowercase
if __name__ == '__main__':
    print(type(ascii_lowercase))
    intStrs = "0123456789"
    for char in ascii_lowercase + intStrs:
        globals()[char+'_dict'] = dict()
        globals()[char+'_file'] = open("./index/{0}.p".format(char), "wb")

    index = pickle.load(open("index.p", 'rb'))

    for key, item in index.items():
        globals()[key[0] + '_dict'][key] = item

    for char in ascii_lowercase + intStrs:
        pickle.dump(globals()[char+'_dict'], globals()[char+'_file'])
        globals()[char + '_file'].close()