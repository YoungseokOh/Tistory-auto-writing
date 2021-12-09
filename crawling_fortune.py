import logging
import time
import urllib
import socket
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import utils
import requests
from datetime import date, datetime
import json

MAX_RETRY = 10
chinese_zodiac = {'1': '쥐띠', '2': '소띠', '3': '호랑이띠', '4': '토끼띠',
                  '5': '용띠', '6': '뱀띠', '7': '말띠', '8': '양띠',
                  '9': '원숭이띠', '10': '닭띠', '11': '개띠', '12': '돼지띠'}

def get_html(html_url, timeout=10, decode='utf-8'):
    for tries in range(MAX_RETRY):
        try:
            with urllib.request.urlopen(html_url, timeout=timeout) as response:
                return response.read()
        except Exception as e:
            logging.warning(str(e) + ',html_url:{0}'.format(html_url))
            if tries < (MAX_RETRY - 1):
                continue
            else:
                print('Has tried {0} times to access url {1}, all failed!'.format(MAX_RETRY, html_url))
                return None


def main(today_date):
    date_str = datetime.strftime(today_date, "%Y-%m-%d")
    if not utils.check_exist('fortune/{}'.format(date_str)):
        utils.make_folder('fortune/{}'.format(date_str))
    for z in range(len(chinese_zodiac)):
        fortune_list_url = 'https://sazoo.com/ss/run/sazoo/ddi/result.php?ddi={}'.format(z+1)
        fortune_list_read = get_html(fortune_list_url)
        bs_Test = BeautifulSoup(fortune_list_read, 'html.parser')
        attrs = {'align' : 'left', 'style' : 'line-height:21px;font-size:12px;color:#4e0101'}
        bs_fortune = bs_Test.find_all('td', attrs=attrs)
        fortune_year_list = []
        fortune_content_list = []
        for i in range(len(bs_fortune)):
            fortune_year_list.append(bs_fortune[i].get_text().split('년생')[0])
            temp_content = utils.remove_slash_ntr(bs_fortune[i].get_text().split('년생')[1])
            fortune_content_list.append(temp_content)
        zodiac_dict = dict(zip(fortune_year_list, fortune_content_list))
        text_json = utils.json_parsing(zodiac_dict)
        with open('fortune/{}/{}'.format(today_date, chinese_zodiac['{}'.format(z + 1)] + '.json'), "w", encoding='utf-8') as fp:
            fp.write(text_json)
        print(zodiac_dict)
    print(f'Crawling is done')
    category_len = len(bs_Test.find_all('a', attrs={'class': 'link_item'}))


if __name__ == '__main__':
    main(date.today())


