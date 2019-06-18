import re
import numpy as np
import requests
from bs4 import BeautifulSoup
from russtress import Accent
from russian_g2p.Grapheme2Phoneme import Grapheme2Phoneme
from russian_g2p.Accentor import Accentor
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder

def initialize_all():
    transcript = Grapheme2Phoneme()
    accent = Accent()
    accent_backup = Accentor()
    encode = OneHotEncoder()
    return transcript, accent, accent_backup, encode

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

def clean_line(line):
    line = re.sub(r'[^-\w\s]', r'', line.lower())
    return re.sub(r'(\W)-|-(\W)', r'\1\2', line)

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
    
def make_basic_vectors(list_of_lines, accent, accent_backup, transcript, encode):
    vectors = np.zeros((1,22))
    for line in list_of_lines:
        vectors = np.append(vectors, line_to_vector(line, accent, accent_backup, transcript), axis=0)
    last_sounds = vectors[...,1:5]
    one_hot_last_sounds = encode.fit_transform(last_sounds).toarray()
    vectors = np.hstack((vectors, one_hot_last_sounds))
    return np.delete(vectors,[1,2,3,4],1)

def make_categories(encode):
    x0 = []
    x1 = []
    x2 = []
    x3 = []
    for feature in encode.get_feature_names():
        if feature.startswith('x0_'):
            x0.append(feature[3:])
        if feature.startswith('x1_'):
            x1.append(feature[3:])
        if feature.startswith('x2_'):
            x2.append(feature[3:])
        if feature.startswith('x3_'):
            x3.append(feature[3:])
    return [x0, x1, x2, x3]

def make_files():
    transcript, accent, accent_backup, encode = initialize_all()
    lines = get_lines()
    with open('original_lines.txt', 'w', encoding='utf-8') as f:
        for line in lines:
            f.write(line + '\n')
    vectors = make_basic_vectors(lines, accent, accent_backup, transcript, encode)
    np.save('vectors.npy', vectors)
    categories = make_categories(encode)
    with open('categories.txt', 'w', encoding='utf-8') as f:
        for category in categories:
            for feature in category:
                f.write(feature + ',')
            f.write('\n')

make_files()

