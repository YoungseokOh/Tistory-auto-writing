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
chinese_zodiac = {'1': '쥐띠', '2': '소띠', '3': '호랑이띠', '4': '토끼띠'
                  }

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
    fortune_list_url = 'https://sazoo.com/ss/run/sazoo/ddi/result.php?ddi=1'
    fortune_list_read = get_html(fortune_list_url)
    bs_Test = BeautifulSoup(fortune_list_read, 'html.parser')
    attrs = {'align' : 'left', 'style' : 'line-height:21px;font-size:12px;color:#4e0101'}
    bs_fortune = bs_Test.find_all('td', attrs=attrs)
    for i in range(bs_fortune):
        bs_fortune[i].get_text()

    category_len = len(bs_Test.find_all('a', attrs={'class': 'link_item'}))


if __name__ == '__main__':
    main(date.today())


