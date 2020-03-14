import pickle
from string import ascii_lowercase
import os
from os import walk
from os.path import isfile, join

if __name__ == "__main__":

    intStrs = "0123456789"
    full_alpha = intStrs + ascii_lowercase
    file_list = []
    file_dict = dict()
    file_indices = dict()

    pickle_dict = dict()
    try:
        os.mkdir("index3")
    except(FileExistsError):
        pass
    try:
        os.mkdir("indexStage2")
    except(FileExistsError):
        pass


    for character in full_alpha:
        #open("index2/" + character + ".txt", 'wb').close()
        file_list.append("index3/" + character + ".txt")
        open("index3/" + character + ".txt", 'wb').close()
        open("indexStage2/" + character + ".p", 'wb').close()
        file_dict["index3/" + character + ".txt"] = open("index3/" + character + ".txt", 'wb')
        pickle_dict[character] = ("indexStage2/" + character + ".p")

    print("Generating Alphabet Dicts")
    for character in full_alpha:
        term_dict = dict()
        for indexerPath, _, files in walk("indexStage1", topdown=True):
            for file_name in files:
                with open(join(indexerPath, file_name), 'rb') as current_file:
                    current_index_dict = pickle.load(current_file)
                    for term in current_index_dict:
                        if term[0] == character:
                            if term not in term_dict:
                                term_dict[term] = dict()
                            # file_dict["index3/" + term[0] + ".txt"].write((term + ',').encode('utf-8'))
                            for key in current_index_dict[term].keys():
                                # file_dict["index3/" + term[0] + ".txt"].write((str(key) + ',').encode('utf-8'))
                                term_dict[term][key] = current_index_dict[term][key]
                                # for val in current_index_dict[term][key]:
                                #    file_dict["index3/" + term[0] + ".txt"].write((str(val) + ',').encode('utf-8'))
                            # file_dict["index3/" + term[0] + ".txt"].write('\n'.encode('utf-8'))

        with open(pickle_dict[character], 'wb') as pickle_file:
            pickle.dump(term_dict, pickle_file)

        print("Alphabet Dict " + character + " complete")

    print("Generating Text Index")
    for character in full_alpha:
        with open(pickle_dict[character], 'rb') as pickle_file:
            character_dict = pickle.load(pickle_file)
            for term in character_dict.keys():
                file_dict["index3/" + character + ".txt"].write(((term + ',').encode('utf-8')))

                for key in character_dict[term].keys():
                    file_dict["index3/" + character + ".txt"].write((str(key) + ',').encode('utf-8'))
                    for val in character_dict[term][key]:
                        file_dict["index3/" + character + ".txt"].write((str(val) + ',').encode('utf-8'))
                file_dict["index3/" + character + ".txt"].write('\n'.encode('utf-8'))

        print("Text file " + character + " complete")


    # with open("index.p", 'rb') as index_pickle:
    #     index = pickle.load(index_pickle)
    # current_character_index = 0
    # current_character = full_alpha[current_character_index]
    # running_total_in_file = 0
    # current_file = open(file_list[current_character_index], 'wb')
    # for term in sorted(index.keys()):
    #     while term[0] != full_alpha[current_character_index]:
    #         current_character_index += 1
    #     if  current_character != full_alpha[current_character_index]:
    #         running_total_in_file = 0
    #         current_character = full_alpha[current_character_index]
    #         current_file.close()
    #         current_file = open(file_list[current_character_index], 'wb')
    #
    #     file_indices[term] = running_total_in_file
    #     current_file.write((term + ',').encode('utf-8'))
    #     for key in index[term].keys():
    #         current_file.write((str(key) + ',').encode('utf-8'))
    #         for val in index[term][key]:
    #             current_file.write((str(val) + ',').encode('utf-8'))
    #     current_file.write('\n'.encode('utf-8'))
    #     running_total_in_file += 1

    for file in file_list:
        position = 0
        print(file)
        with open(file, 'r') as f:

            line = f.readline()
            while line != '':
                file_indices[line.split(',')[0]] = position
                position = f.tell()
                line = f.readline()


    pickle.dump(file_indices, open("file_indices_2.p", 'wb'))
