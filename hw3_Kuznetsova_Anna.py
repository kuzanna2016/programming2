import urllib.request
import re
import os
import shutil


def find_articles():
    all_articles = []
    for number in range(0, 240, 12):
        response = urllib.request.urlopen(f'https://kvgazeta.ru/articles.html?start={number}')
        text = response.read().decode('utf-8')
        articles = re.findall(r'''<h2 class="article-title" itemprop="headline">\n\t{5}<a href="(.*?)"''', text)
        all_articles.extend(articles)
    return all_articles


def open_page(url):
    page_url = f'https://kvgazeta.ru{url}'
    response = urllib.request.urlopen(page_url)
    html = response.read().decode('utf-8')
    return html


def get_metadata(html):
    author = re.search(r'<meta itemprop="name" content="(.*?)"/>', html).group(1)
    if author == 'kvgazeta.ru':
        author = ''
    title = re.search(r'<meta property="og:title" content="(.*?)" />', html).group(1)
    title_for_file = re.sub(r'[\\|/:?*"<>+]', '', title)
    date_no_form = re.search(r'<meta property="article:published_time" content="(\d{4})-(\d{2})-(\d{2})', html)
    date = f'{date_no_form.group(3)}.{date_no_form.group(2)}.{date_no_form.group(1)}'
    url = re.search(r'<base href="(.*?)" />', html).group(1)
    year = date_no_form.group(1)
    path = f'newspaper\plain\{year}\{date_no_form.group(2)}\{title_for_file}.txt'
    metadata = [path, author, title, date, url, year, title_for_file]
    return metadata


def folder_maker(meta):
    directory = f'newspaper\%s\{meta[5]}\{meta[3][3:5]}'
    if not os.path.exists(directory % 'plain'):
        os.makedirs(directory % 'plain')
        os.makedirs(directory % 'mystem-xml')
        os.makedirs(directory % 'mystem-plain')



def append_to_csv(metadata):
    row = f'{metadata[0]}\t{metadata[1]}\t{metadata[2]}\t{metadata[3]}\tпублицистика\t\tнейтральный\tн-возраст\tн-уровень\tгородская\t{metadata[4]}\tКанские ведомости\t{metadata[5]}\tгазета\tРоссия\tКрасноярский край\tru\n'
    with open('newspaper\metadata.csv', 'a', encoding='utf-8') as f:
        f.write(row)


def plain_text(html, meta):
    text = re.search(r'<section class="article-content clearfix" itemprop="articleBody">(.*?)</section>', html,
                     flags=re.DOTALL).group(1)
    text_no_tags = re.sub(r'<.*?>', r'', text)
    text_plain = re.sub(r'(\s)\s+', r'\1', text_no_tags)
    title = meta[2]
    with open('input.txt', 'w', encoding='utf-8') as f:
        f.write(text_plain)
    with open(meta[0], 'w', encoding='utf-8') as f:
        f.write(f'''@au {meta[1]}
@ti {title}
@da {meta[3]}
@topic None
@url {meta[4]}
{text_plain}''')


def mystem_xml(meta):
    os.system(fr'mystem.exe -ldcni --eng-gr input.txt output.xml')
    directory = re.sub('plain', 'mystem-xml', meta[0])
    shutil.move(f'output.xml', directory)


def mystem_plain_text(meta):
    os.system(fr'mystem.exe -ldcni --eng-gr input.txt output.txt')
    directory = re.sub('plain', 'mystem-plain', meta[0])
    shutil.move(f'output.txt', directory)


def all_together():
    if not os.path.exists('newspaper'):
        os.mkdir('newspaper')
    with open('newspaper\metadata.csv', 'w', encoding='utf-8') as f:
        f.write('path\tauthor\theader\tcreated\tsphere\ttopic\tstyle\taudience_age\taudience_level\taudience_size\tsource\tpublication\tpubl_year\tmedium\tcountry\tregion\tlanguage\n')
    articles = find_articles()
    for article in articles:
        html = open_page(article)
        meta = get_metadata(html)
        folder_maker(meta)
        append_to_csv(meta)
        plain_text(html, meta)
        mystem_plain_text(meta)
        mystem_xml(meta)
    os.remove('input.txt')


if __name__ == '__main__':
    all_together()