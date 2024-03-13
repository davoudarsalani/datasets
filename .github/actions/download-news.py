#!/usr/bin/env python

from copy import deepcopy
from getopt import getopt
from json import load as load, dumps as dumps
from os import path
from re import match, sub
from sys import argv
from urllib.request import urlopen
from uuid import uuid4


INVALID_IMG_URLS = ['', 'null', 'None', None]

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

    main_file     = f'./news/api-news/{source}.json'
    main_file_2   = f'./news/api-news/{source}-2.json'
    main_file_3   = f'./news/api-news/{source}-3.json'
    dl_successful = False
    dl_try        = 1

    while not dl_successful and dl_try <= 5:
        try:

            if path.exists(main_file):
                print('reading current news')
                with open(main_file) as opened:
                    already_1 = load(opened)
                    already_1_uuids = [_.get('short_uuid', '') for _ in already_1]

                already_1__trimmed = deepcopy(already_1)
                for dict_ in already_1__trimmed:
                    if dict_.get('short_uuid'):
                        del dict_['short_uuid']
            else:
                already_1          = []
                already_1_uuids    = []
                already_1__trimmed = []




            if path.exists(main_file_2):
                print('reading previous news')
                with open(main_file_2) as opened:
                    already_2 = load(opened)
                    already_2_uuids = [_.get('short_uuid', '') for _ in already_2]

                already_2__trimmed = deepcopy(already_2)
                for dict_ in already_2__trimmed:
                    if dict_.get('short_uuid'):
                        del dict_['short_uuid']
            else:
                already_2          = []
                already_2_uuids    = []
                already_2__trimmed = []

            if path.exists(main_file_3):
                print('reading previous news')
                with open(main_file_3) as opened:
                    already_3 = load(opened)
                    already_3_uuids = [_.get('short_uuid', '') for _ in already_3]

                already_3__trimmed = deepcopy(already_3)
                for dict_ in already_3__trimmed:
                    if dict_.get('short_uuid'):
                        del dict_['short_uuid']
            else:
                already_3          = []
                already_3_uuids    = []
                already_3__trimmed = []

            ######################################

            print('downloading news with urlopen')
            resp = urlopen(url)

            print('parsing the news')
            resp = load(resp)

            print('getting status')
            stts = resp.get('status')
            if stts:  ## if statement because gnews has no 'status' key
                if not match(success_regex, stts):
                    print(f'ERROR: Status = {stts}, meaning downloading was not successful')
                    exit(1)

            ######################################

            print('appending new news')
            new_uuids = []
            new_news = resp.get(news_key, [])
            for nn in new_news:
                img_url = nn.get('image')     or \
                          nn.get('image_url') or \
                          nn.get('urlToImage')
                # img_url = re.sub(r'\?.*', '', img_url)

                if img_url in INVALID_IMG_URLS:
                    continue

                if nn not in already_1__trimmed and \
                   nn not in already_2__trimmed and \
                   nn not in already_3__trimmed:

                    ## add short_uuid
                    new_uuid_is_dupl = True
                    while new_uuid_is_dupl:
                        new_uuid = hex(int(uuid4().time_low))[2:10]
                        if  new_uuid not in already_1_uuids and \
                            new_uuid not in already_2_uuids and \
                            new_uuid not in already_3_uuids and \
                            new_uuid not in new_uuids:
                            new_uuid_is_dupl = False

                    ## add nn to already_1__trimmed before adding short_uuid to it
                    ## (keep above JUMP_1)
                    already_1__trimmed.append(nn)

                    nn['short_uuid'] = new_uuid  ## JUMP_1
                    already_1.append(nn)
                    new_uuids.append(new_uuid)

            ######################################

            print(f'write to {main_file}')
            with open(main_file, 'w') as opened:
                dumped = dumps(already_1, indent=2)
                opened.write(dumped + '\n')

            dl_successful = True

        except Exception as exc:
            print(f'ERROR in try {dl_try}: {exc!r}')

        dl_try += 1

if __name__ == '__main__':
    script_args = argv[1:]
    success_regex = '^([Oo][Kk]|[Ss][Uu][Cc][Cc][Ee][Ss][Ss])$'
    null_regex = '^([Nn][Oo][Nn][Ee]|[Nn][Uu][Ll][Ll])$'

    main()
