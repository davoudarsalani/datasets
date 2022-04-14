#!/usr/bin/env python

from getopt import getopt
from json import load as j_load, dumps as j_dumps
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
    try:
        ## read current *.json file:
        print('reading current news')
        with open(main_file) as main:
            orig_content = j_load(main)

        print('downloading news with urlopen')
        resp = urlopen(url)

        print('parsing news')
        resp = j_load(resp)

        stts = resp.get('status', None)  ## None because gnews has no status
        if stts:
            if not match(success_regex, stts):
                print(f'ERROR: Status = {stts}, meaning downloading wsa not successful')
                exit(1)

        print('appending news')
        news_list = resp[news_key]
        for news in news_list:
            orig_content.append(news)

        print('removing duplicates')
        print(f'count before removing: {len(orig_content)}')
        final_list = []
        for entry in orig_content:
            if entry not in final_list:
                final_list.append(entry)
        print(f'count after removing: {len(final_list)}')
        print()

        print('write')
        with open(main_file, 'w') as main2:
            dumped = j_dumps(final_list, indent=2)
            main2.write(dumped+'\n')

    except Exception as exc:
        print(f'ERROR: {exc!r}')


if __name__ == '__main__':
    script_args = argv[1:]
    success_regex = '^([Oo][Kk]|[Ss][Uu][Cc][Cc][Ee][Ss][Ss])$'
    null_regex = '^([Nn][Oo][Nn][Ee]|[Nn][Uu][Ll][Ll])$'

    main()
