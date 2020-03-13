import pickle
from string import ascii_lowercase
import os

if __name__ == "__main__":
    intStrs = "0123456789"
    full_alpha = ascii_lowercase + intStrs
    file_list = []
    file_indices = {}
    try:
        os.mkdir("index2")
    except(FileExistsError):
        pass
    for character in full_alpha:
        open("index2/" + character + ".txt", 'w').close()
        file_list.append("index2/" + character + ".txt")
    with open("index.p", 'rb') as index_pickle:
        index = pickle.load(index_pickle)
    current_character_index = 0
    current_character = full_alpha[current_character_index]
    running_total_in_file = 0

    for term in sorted(index.keys()):
        while term[0] != full_alpha[current_character_index]:
            current_character_index += 1
        current_file = open(file_list[current_character_index], 'w')
        if current_character != full_alpha[current_character_index]:
            running_total_in_file = 0
            current_character = full_alpha[current_character_index]
            current_file.close()
            current_file = open(file_list[current_character_index], 'w')

        current_file.write(term + ',')
        for key in index[term].keys():
            print(index[term])
            print(key)
            current_file.write(str(key) + ',')
            for val in index[term][key]:
                current_file.write(str(val) + ',')
        current_file.write('/n')
        running_total_in_file += 1
        if running_total_in_file > 20:
            break

        #file_indices[file_list[current_character_index]]


