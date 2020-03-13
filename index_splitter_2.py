import pickle
from string import ascii_lowercase
import os

if __name__ == "__main__":

    intStrs = "0123456789"
    full_alpha = intStrs + ascii_lowercase
    file_list = []
    file_indices = {}
    try:
        os.mkdir("index2")
    except(FileExistsError):
        pass

    for character in full_alpha:
        open("index2/" + character + ".txt", 'wb').close()
        file_list.append("index2/" + character + ".txt")
    with open("index.p", 'rb') as index_pickle:
        index = pickle.load(index_pickle)
    current_character_index = 0
    current_character = full_alpha[current_character_index]
    running_total_in_file = 0
    current_file = open(file_list[current_character_index], 'wb')
    for term in sorted(index.keys()):
        while term[0] != full_alpha[current_character_index]:
            current_character_index += 1
        if  current_character != full_alpha[current_character_index]:
            running_total_in_file = 0
            current_character = full_alpha[current_character_index]
            current_file.close()
            current_file = open(file_list[current_character_index], 'wb')

        file_indices[term] = running_total_in_file
        current_file.write((term + ',').encode('utf-8'))
        for key in index[term].keys():
            current_file.write((str(key) + ',').encode('utf-8'))
            for val in index[term][key]:
                current_file.write((str(val) + ',').encode('utf-8'))
        current_file.write('\n'.encode('utf-8'))
        running_total_in_file += 1

    for file in file_list:
        position = 0
        print(file)
        with open(file, 'r') as f:

            line = f.readline()
            while line != '':
                file_indices[line.split(',')[0]] = position
                position = f.tell()
                line = f.readline()


    pickle.dump(file_indices, open("file_indices.p", 'wb'))
