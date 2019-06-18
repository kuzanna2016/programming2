#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import numpy as np
import requests
from bs4 import BeautifulSoup
from russtress import Accent
from russian_g2p.Grapheme2Phoneme import Grapheme2Phoneme
from russian_g2p.Accentor import Accentor
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder


# In[2]:


def initialize_all():
    transcript = Grapheme2Phoneme()
    accent = Accent()
    accent_backup = Accentor()
    with open('categories.txt', encoding='utf-8') as f:
        categories = f.read().splitlines()
    categories_new = [[categ.split(',')[:-1]] for categ in categories]
    encode = OneHotEncoder(categories=categories_new)
    return transcript, accent, accent_backup, encode


# In[3]:


def get_lines():
    result = requests.get('https://rupoem.ru/axmatova/all.aspx')
    html = result.text
    marshak = BeautifulSoup(html,'html.parser')
    all_lines = []
    for poem in marshak.find_all('div', class_="poem-text"):
        poem_text = poem.string
        if poem_text == None:
            continue
        poem_lines = poem_text.splitlines()
        for line in poem_lines:
            if line == '' or re.search(r'[а-яёА-ЯЁ]', line) == None:
                continue
            if line in all_lines:
                continue
            if re.search(r'[a-zA-Z]', line) != None:
                continue
            all_lines.append(line)
    return all_lines


# In[4]:


def clean_line(line):
    line = re.sub(r'[^-\w\s]', r'', line.lower())
    return re.sub(r'(\W)-|-(\W)', r'\1\2', line)


# In[5]:


def line_to_vector(line, accent, accent_backup, transcript):
    line = clean_line(line)
    accented_line = accent.put_stress(line)
    words = re.split(r'[-\s]', accented_line)
    for word in words:
        if "'" not in word:
            corrected_word = accent.put_stress(word)
            accented_line = accented_line.replace(word, corrected_word)
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


# In[6]:


def make_basic_vectors(list_of_lines, accent, accent_backup, transcript, encode):
    vectors = np.zeros((1,22))
    for line in list_of_lines:
        vectors = np.append(vectors, line_to_vector(line, accent, accent_backup, transcript), axis=0)
    last_sounds = vectors[...,1:5]
    one_hot_last_sounds = encode.fit_transform(last_sounds).toarray()
    vectors = np.hstack((vectors, one_hot_last_sounds))
    return np.delete(vectors,[1,2,3,4],1)


# In[7]:


def make_vector_from_input_line(line, accent, accent_backup, transcript, encode):
    vector = line_to_vector(line, accent, accent_backup, transcript)
    last_sounds = vector[0][1:5]
    features = encode.get_feature_names().tolist()
    for n, sound in enumerate(last_sounds):
        sound = 'x' + str(n) + '_' + sound
        if sound not in features:
            sound = sound[3:]
            np.place(last_sounds, last_sounds == sound, [0.0])
    one_hot_last_sounds = encode.transform(last_sounds.reshape(1, -1)).toarray()
    vector = np.hstack((vector, one_hot_last_sounds))
    return np.delete(vector,[1,2,3,4],1)


# In[8]:


def from_input_line_to_indxs(line, list_of_lines, accent, accent_backup, transcript, vectors,encode):
    vector_of_line = make_vector_from_input_line(line.lower(), accent, accent_backup, transcript, encode)
    nn = NearestNeighbors()
    nn.fit(vectors)
    return nn.kneighbors(vector_of_line.reshape(1, -1))[1][0]


# In[25]:


def chose_one(line, lines, indxs):
    line = clean_line(line).split()
    orig_lines = []
    for indx in indxs:
        orig_line = clean_line(lines[indx - 1]).split()
        if orig_line[-1] != line[-1]:
            orig_lines.append(lines[indx - 1])
    return re.sub(r'[,\- —]*?$', r'', orig_lines[0])


# In[10]:


def check_the_line(line):
    while (line == '') or (re.search(r'[а-яёА-ЯЁ]', line) == None) or (re.search(r'[a-zA-Z]', line) != None):
        print('so sad, but you are a bad poet, try again')
        line = str(input())
    return line

def make_files():
    transcript, accent, accent_backup, encode = initialize_all()
    lines = get_lines()
    with open('original_lines.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    vectors = make_basic_vectors(lines, accent, accent_backup, transcript, encode)
    np.save('vectors.npy', vectors)

def from_line_to_rythm(input_line):
    vectors = np.load('vectors.npy')
    with open('original_lines.txt', encoding='utf-8') as f:
        lines = f.read().splitlines()
    transcript, accent, accent_backup, encode = initialize_all()
    input_line = check_the_line(input_line)
    neighbor_indx = from_input_line_to_indxs(input_line, lines, accent, accent_backup, transcript, vectors, encode)
    return chose_one(input_line, lines, neighbor_indx)

if __name__ == '__main__':
    make_files()
    from_line_to_rythm(input())

with open('categories.txt', encoding='utf-8') as f:
    categories = f.read().splitlines()
categories_new = [[categ.split(',')[:-1]] for categ in categories]
