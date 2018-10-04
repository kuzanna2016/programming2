import json
import urllib.request


def choice_of_user(list_of_users):
    user = input('Выберите одного из пользователей, с которым хотите работать:')
    while user not in list_of_users:
        user = input('Введите точное имя пользователя из списка:')
    print(f'\nВы выбрали пользователя {user}.\n')
    return user


def get_data_from_user(user, type_of_data):
    token = ""  # сюда надо вставить ваш токен
    data = []
    if type_of_data == 'user':
        url = f'https://api.github.com/users/{user}?access_token={token}'
        response = urllib.request.urlopen(url)
        text = response.read().decode('utf-8')
        data = json.loads(text)
    else:
        i = 1
        while True:
            url = f'https://api.github.com/users/{user}/{type_of_data}?access_token={token}&page={i}'
            response = urllib.request.urlopen(url)
            text = response.read().decode('utf-8')
            a = json.loads(text)
            if not a:
                break
            data.extend(a)
            i += 1
    return data


def repos_names_description(user):
    data = get_data_from_user(user, 'repos')
    print('Вот список его репозиториев и описаний:\n')
    for i in data:
        description = i['description']
        if description is None:
            description = 'описания нет'
        print(f"\t{i['name']}: {description}")


def languages_per_user(user):
    repositories = get_data_from_user(user, 'repos')
    lang_reps = {}
    for rep in repositories:
        if str(rep['language']) == 'None':
            continue
        if rep['language'] not in lang_reps:
            lang_reps[rep['language']] = []
        lang_reps[rep['language']].append(rep['name'])
    return lang_reps


def print_languages_per_user(lang_repos_dict):
    print('Пользователь пишет на ' + ', '.join(str(key) for key in lang_repos_dict.keys()) + '\n')
    for language, repos in lang_repos_dict.items():
        print(f'Язык {language} используется в репозитории %s.' % ', '.join(repos))


def most_repos(user_list):
    repos_per_user = {}
    for user in user_list:
        data = get_data_from_user(user, 'user')
        repos_number = data['public_repos']
        repos_per_user[user] = repos_number
    username = key_with_highest_value(repos_per_user)
    print(f'Больше всего репозиториев у пользователя {username} - {repos_per_user[username]}.\n')


def popular_languages(user_list):
    languages = {}
    for user in user_list:
        data = languages_per_user(user)
        for lang, value in data.items():
            if lang not in languages:
                languages[lang] = 0
            languages[lang] += len(value)
    the_most_popular = key_with_highest_value(languages)
    print(f'Самый популярный язык среди пользователей из списка - {the_most_popular}.\n')


def key_with_highest_value(dic):
    v = list(dic.values())
    k = list(dic.keys())
    return k[v.index(max(v))]


def most_followers(user_list):
    followers_per_user = {}
    for user in user_list:
        data = get_data_from_user(user, 'user')
        followers_per_user[user] = data['followers']
    username = key_with_highest_value(followers_per_user)
    print(f'Больше всего фолловеров у пользователя {username} - {followers_per_user[username]}.\n')


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
    action = input('Введите номер пункта: ')
    actions = ['1', '2', '3', '4', '5']
    while action not in actions:
        action = input('Введите номер пункта цифрой: ')
    if action == '1':
        repos_names_description(choice_of_user(list_of_users))
    elif action == '2':
        print_languages_per_user(languages_per_user(choice_of_user(list_of_users)))
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
