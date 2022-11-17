#!/usr/bin/env python

from getopt import getopt
from json import load as j_load, dumps as j_dumps
from os import path
from re import match, sub
from sys import argv
from urllib.request import urlopen


def normalize(text) -> str:
    ## mormalizing borrowed from download.py script:
    text_normalized = text.lower()
    text_normalized = sub(r'[\s_]', r'-', text_normalized)  ##    ,-- \w does not include _
    text_normalized = sub(r'[^\w-]', r'', text_normalized)  ## <--'-- that's why _ is included in the previous command
    text_normalized = sub(r'-+', r'-', text_normalized)

    return text_normalized


def getopts() -> None:
    global url, source, news_key

    try:
        duos, duos_long = getopt(
            script_args,
            's:u:n:',
            ['source=', 'url=', 'news-key='],
        )
    except Exception as exc:
        print(f'ERROR in getopts: {exc!r}')
        exit()

    for opt, arg in duos:
        if opt in ('-s', '--source'):  ## newsdata/newsapi/etc.
            source = normalize(arg)
        elif opt in ('-u', '--url'):
            url = arg
        elif opt in ('-n', '--news-key'):  ## articles/news/results/etc.
            news_key = arg


def main() -> None:
    getopts()

    main_file = f'./news/api-news/{source}.json'
    previous  = f'./news/api-news/{source}-2.json'
    final_list = []

    try:
        if path.exists(main_file):
            print('reading current news')
            with open(main_file) as main:
                current_news = j_load(main)
        else:
            current_news = []

        if path.exists(previous):
            print('reading previous news')
            with open(previous) as previous_opened:
                previous_news = j_load(previous_opened)
        else:
            previous_news = []

        print('downloading news with urlopen')
        resp = urlopen(url)

        print('parsing the news')
        resp = j_load(resp)

        stts = resp.get('status', None)  ## None because gnews has no status
        if stts:
            if not match(success_regex, stts):
                print(f'ERROR: Status = {stts}, meaning downloading was not successful')
                exit(1)

        print('appending current news')
        for cn in current_news:
            if cn not in previous_news and \
               cn not in final_list:
                final_list.append(cn)

        print('appending new news')
        new_news = resp[news_key]
        for nn in new_news:
            if nn not in current_news and \
               nn not in previous_news and \
               nn not in final_list:
                final_list.append(nn)

        print(f'write to {main_file}')
        with open(main_file, 'w') as main2:
            dumped = j_dumps(final_list, indent=2)
            main2.write(dumped + '\n')

    except Exception as exc:
        print(f'ERROR: {exc!r}')


if __name__ == '__main__':
    script_args = argv[1:]
    success_regex = '^([Oo][Kk]|[Ss][Uu][Cc][Cc][Ee][Ss][Ss])$'
    null_regex = '^([Nn][Oo][Nn][Ee]|[Nn][Uu][Ll][Ll])$'

    main()
