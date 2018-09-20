import random


def load_theme(theme):
    with open(theme + '.txt', encoding='utf-8') as f:
        words = f.read().splitlines()
        return words[random.randint(0, len(words)-1)]


def game(word, lives):
    letters = []
    for letter in word:
        if letter not in letters:
            letters.append(letter)

    already_told_letters = []
    while lives > 0:
        writing_letters(word, letters)

        a = correct_input()

        if a in already_told_letters:
            print('Эта буква уже была!')
        else:
            if a in letters:
                print('Есть такая буква!')
                letters.remove(a)
            else:
                print('Такой буквы нет(')
                lives -= 1
        already_told_letters.append(a)
        tries(lives)
        draw_a_hanger(lives)

        if len(letters) == 0:
            print('Ура! Победа!')
            break

    if lives == 0:
        print('Кто-то повесился...')


def writing_letters(word, letters):
    for letter in word:
        if letter in letters:
            print('_', end=' ')
        else:
            print(letter, end=' ')
    print('\n')


def draw_a_hanger(lives):
    head, body, left, right = '___\n | \n 0\n', '|', '/', '\\'
    parts = [head, left, body, right, left, ' ' + right]
    current_body = parts[:len(parts) - lives]
    if len(current_body) >= 4:
        current_body.insert(4, '\n')
    for i in range(len(current_body)):
        print(current_body[i], end='')
    print('\n')


def tries(lives):
    if lives == 5:
        print('Осталось 5 попыток')
    elif lives in [4, 3, 2]:
        print(f'Осталось {lives} попытки')
    elif lives == 1:
        print('Осталась 1 попытка')


def correct_input():
    a = input('Введите одну букву: ')
    if a.isalpha() and len(a) == 1:
        return a
    else:
        correct_input()


def choose_theme():
    themes = ['приправы', 'породы собак', 'породы кошек']
    for theme in themes:
        print(theme)
    the_theme = input('Выберите одну из предложенных тем: ')
    while the_theme not in themes:
        the_theme = input('Напишите, пожалуйста, точное название темы: ')
    return the_theme


if __name__ == '__main__':
    n = 6
    z = 1
    while True:
        the_word = load_theme(choose_theme())
        print(f'У вас есть {n} попыток, чтобы угадать слово длинной {len(the_word)} букв')
        game(the_word, n)
        z = int(input('Хотите сыграть еще?\n1 - Да\n0 - Нет\n'))
        if z == 0:
            break
