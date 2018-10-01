import json
import urllib.request


def choice_of_user(list_of_users):
    user = input('Выберите одного из пользователей, с которым хотите работать:')
    while user not in list_of_users:
        user = input('Введите точное имя пользователя из списка:')
    print('')
    print(f'Вы выбрали пользователя {user}.\n')
    return user


def get_data_from_user(user, type_of_data):
    token = ""  # сюда надо вставить ваш токен
    data = []
    if type_of_data == 'user':
        url = f'https://api.github.com/users/{user}?access_token={token}'
        request = urllib.request.Request(url)
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        data = json.loads(text)
    else:
        i = 1
        while True:
            url = f'https://api.github.com/users/{user}/{type_of_data}?access_token={token}&page={i}'
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(url)
            text = response.read().decode('utf-8')
            a = json.loads(text)
            i += 1
            if not a:
                break
            data.extend(a)
    return data


def repos_names_description(user):
    data = get_data_from_user(user, 'repos')
    print('Вот список его репозиториев и описаний:')
    for i in data:
        description = i['description']
        if description is None:
            description = 'описания нет'
        print('\t%s: %s' % (i['name'], description))
    print('')


def languages_per_user(user):
    data = get_data_from_user(user, 'repos')
    languages = []
    repos_per_languages = {}
    for i in data:
        name_of_language = str(i['language'])
        if name_of_language == 'None':
            continue
        if name_of_language not in languages:
            languages.append(name_of_language)
    print('Пользователь пишет на %s.\n' % ', '.join(languages))
    for language in languages:
        repos = []
        for i in data:
            if str(i['language']) == language:
                repos.append(str(i['name']))
        repos_per_languages[language] = repos
    for language, repos in repos_per_languages.items():
        print(f'Язык {language} используется в репозитории %s.' % ', '.join(repos))
    print('')


def most_repos(user_list):
    repos_per_user = {}
    for user in user_list:
        data = get_data_from_user(user, 'user')
        repos_number = data['public_repos']
        repos_per_user[user] = repos_number
    for user in sorted(repos_per_user, key=repos_per_user.get, reverse=True):
        print(f'Больше всего репозиториев у пользователя {user} - {repos_per_user[user]}.\n')
        break


def popular_languages(user_list):
    languages = {}
    for user in user_list:
        data = get_data_from_user(user, 'repos')
        for i in data:
            if i['language'] is None:
                continue
            if i['language'] not in languages:
                languages[i['language']] = 1
            else:
                languages[i['language']] += 1
    for language in sorted(languages, key=languages.get, reverse=True):
        print(f'Самый популярный язык среди пользователей из списка - {language}.\n')
        break


def most_followers(user_list):
    followers_per_user = {}
    for user in user_list:
        data = get_data_from_user(user, 'user')
        followers_per_user[user] = data['followers']
    for user in sorted(followers_per_user, key=followers_per_user.get, reverse=True):
        print(f'Больше всего подписчиков у пользователя {user} - {followers_per_user[user]}.')
        break


def choice_of_action(list_of_users):
    print('Вот список доступных пользователей:')
    for user in list_of_users:
        print(user)
    print('''\nЧто вы хотите сделать?
    1.Вывести список репозиториев одного из пользователей.
    2.Вывести список языков одного из пользователей и репозитории, в которых они используются.
    3.Узнать, у кого из пользователей в списке больше всего репозиториев.
    4.Узнать, какой язык самый популярный среди пользователей списка.
    5.Узнать, у кого из пользователей списка больше всего подписчиков.\n''')
    action = input('Введите номер пункта:')
    actions = ['1', '2', '3', '4', '5']
    while action not in actions:
        action = input('Введите номер пункта цифрой:')
    if action == '1':
        repos_names_description(choice_of_user(list_of_users))
    elif action == '2':
        languages_per_user(choice_of_user(list_of_users))
    elif action == '3':
        most_repos(list_of_users)
    elif action == '4':
        popular_languages(list_of_users)
    elif action == '5':
        most_followers(list_of_users)


if __name__ == "__main__":
    users = ['elmiram', 'maryszmary', 'lizaku', 'nevmenandr', 'ancatmara', 'roctbb', 'akutuzov', 'agricolamz', 'lehkost', 'kylepjohnson', 'mikekestemont', 'demidovakatya', 'shwars', 'JelteF', 'timgraham', 'arogozhnikov', 'jasny', 'bcongdon', 'whyisjake', 'gvanrossum']  # сюда нужно вставить список пользователей
    while True:
        choice_of_action(users)
        z = int(input('Хотите попробовать еще?\n1 - Да\n0 - Нет\n'))
        if z == 0:
            break
