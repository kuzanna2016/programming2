import re
import numpy as np
import requests
from bs4 import BeautifulSoup
#from russtress import Accent
from russian_g2p.Grapheme2Phoneme import Grapheme2Phoneme
from russian_g2p.Accentor import Accentor
from sklearn.neighbors import NearestNeighbors

def initialize_all():
    transcript = Grapheme2Phoneme()
#    accent = Accent()
    accent_backup = Accentor()
    return transcript, accent_backup

def encode(array, categories):
    new_array = []
    array = array.tolist() # [['A', 'B', 'C', 'D']]
    for cat_i, category in enumerate(categories):
        x = []
        if array[0][cat_i] in category[0]:
            for feature in category[0]:
                if array[0][cat_i] == feature:
                    x.append(1)
                else:
                    x.append(0)
        else:
            x = np.zeros(len(category))
        new_array = np.append(new_array, np.array(x))
    return np.array(new_array).reshape(1,-1)
    
    
def clean_line(line):
    line = re.sub(r'[^-\w\s]', r'', line.lower())
    return re.sub(r'(\W)-|-(\W)', r'\1\2', line)

def line_to_vector(line, accent_backup, transcript):
    line = clean_line(line)
    words = re.split(r'[-\s]', line)
    for word in words:
        accent_word = accent_backup.do_accents([[word]])[0][0].replace("+", "'")
        accented_line = line.replace(word, accent_word)
    if re.search(r"[^ёуеыаоэяию]'", accented_line) != None:
        troubled_word = re.search(r"(\w*?[^ёуеыаоэяию]'\w*?)(\W|$)", accented_line).group(1)
        changed_troubled_word = accent_backup.do_accents([[troubled_word.replace("'","")]])[0][0]
        accented_line = accented_line.replace(troubled_word, changed_troubled_word.replace("+","'"))
    vowels = re.findall(r"[ёуеыаоэяию]'?", accented_line)
    # если нет гласных, добавляем пустой вектор, только с окончаниями
    if len(vowels) == 0:
        transcription = transcript.phrase_to_phonemes(line)
        if len(transcription) < 4:
            last_4 = ['0','0','0','0']
        else:
            last_4 = transcription[-4:]
        result = np.append([0], np.array(last_4))
        return result
    else:
        transcription = transcript.phrase_to_phonemes(accented_line.replace("'","+"))
        if len(transcription) < 4:
            last_4 = transcription
            while len(last_4) != 4:
                last_4.insert(0, '0')
        else:
            last_4 = transcription[-4:]
        idx_vowels = []
        for n, vowel in enumerate(vowels):
            if "'" in vowel:
                idx_vowels.append(1)
            else:
                idx_vowels.append(0)
        result = np.append([len(vowels)], np.array(last_4))
        while len(idx_vowels) < 17:
            idx_vowels.append(0)
        while len(idx_vowels) > 17:
            idx_vowels.pop(0)
        return np.append(result, np.array(idx_vowels)).reshape(1,-1)
    
def make_vector_from_input_line(line, accent_backup, transcript, categories):
    vector = line_to_vector(line, accent_backup, transcript)
    last_sounds = vector[0][1:5]
    for n, sound in enumerate(last_sounds):
        if sound not in categories[n][0]:
            np.place(last_sounds, last_sounds == sound, [0.0])
    one_hot_last_sounds = encode(last_sounds.reshape(1, -1), categories)
    vector = np.concatenate((vector, one_hot_last_sounds), axis=1)
    return np.delete(vector,[1,2,3,4],1)

def from_input_line_to_indxs(line, list_of_lines, accent_backup, transcript, vectors, categories):
    vector_of_line = make_vector_from_input_line(line.lower(), accent_backup, transcript, categories)
    nn = NearestNeighbors()
    nn.fit(vectors)
    return nn.kneighbors(vector_of_line.reshape(1, -1))[1][0]

def chose_one(line, lines, indxs):
    line = clean_line(line).split()
    orig_lines = []
    for indx in indxs:
        orig_line = clean_line(lines[indx - 1]).split()
        if orig_line[-1] != line[-1]:
            orig_lines.append(lines[indx - 1])
    return re.sub(r'[,\- —]*?$', r'', orig_lines[0])

def from_line_to_rythm(input_line):
    vectors = np.load('vectors.npy')
    with open('original_lines.txt', encoding='utf-8') as f:
        lines = f.read().splitlines()
    with open('categories.txt', encoding='utf-8') as f:
        categories = f.read().splitlines()
    categories = [[categ.split(',')[:-1]] for categ in categories]
    transcript, accent_backup = initialize_all()
    neighbor_indx = from_input_line_to_indxs(input_line, lines, accent_backup, transcript, vectors, categories)
    return chose_one(input_line, lines, neighbor_indx)

print(from_line_to_rythm('эх брадобрей ты мне приятен'))