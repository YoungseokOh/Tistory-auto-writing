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


def get_html(html_url, timeout=20, decode='utf-8'):
    for tries in range(MAX_RETRY):
        try:
            with urllib.request.urlopen(html_url, timeout=timeout) as response:
                return response.read()
        except Exception as e:
            logging.warning(str(e) + ',html_url:{0}'.format(html_url))
            print(f'Connection warning! tried : {tries}')
            if tries < (MAX_RETRY - 1):
                continue
            else:
                print('Has tried {0} times to access url {1}, all failed!'.format(MAX_RETRY, html_url))
                return None


def day_crawling(url, category_name, today_date, date_text):
    socket.setdefaulttimeout(20)
    test_url = url
    req = requests.get(test_url)
    if req.status_code == 404:
        pass
    res_read = get_html(test_url)
    bs = BeautifulSoup(res_read, 'html.parser')
    if not req.status_code == 404:
        # print(bs.find('meta', property="article:published_time").get('content')[:10])
        if not date.fromisoformat(bs.find('meta', property="article:published_time").get('content')[:10]) == today_date:
            pass
    title = bs.find('title').get_text()
    signal = []
    questions = []
    answer = []
    results_count = 0
    results = bs.find_all('p')
    for i in results:
        # print(i.get_text())
        if '정답은' in i.get_text():
            if '블로그 이용방법 숙지하기(클릭)' in i.get_text():
                continue
            else:
                questions.append(results[results_count-1].get_text(strip=True))
                answer.append(results[results_count].get_text(strip=True))
                results_count += 1
        else:
            results_count += 1
            continue
    questions = utils.remove_xa0(questions)
    questions = utils.remove_quo_marks(questions)
    questions = utils.remove_bracket(questions)
    data = {}
    data['post'] = []
    data['count'] = [len(questions)]
    for n in range(len(questions)):
        data['post'].append({"question": questions[n], "answer":answer[n]})
    with open("./answer/{}/{}/{}.json".format(category_name, today_date, title), 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    print(title)
    print(questions)
    print(answer)


def main(today_date):
    # excluded name
    ex_name = []
    # date_str -> "%y-%m-%d" or date.today()
    # date_str = date.today()
    # if date_str.__class__.__name__ == 'date':
    #     today_date = date_str
    # else:
    #     today_date = datetime.strptime(date_str, "%Y-%m-%d")
    date_str = datetime.strftime(today_date, "%Y-%m-%d")
    blog_list_url = 'https://luckyquiz.tistory.com/category/'
    blog_list_read = get_html(blog_list_url)
    bs_Test = BeautifulSoup(blog_list_read, 'html.parser')
    category_len = len(bs_Test.find_all('a', attrs={'class': 'link_item'}))
    for cate_num in range(category_len):
        category_name = utils.remove_slash_ntr(bs_Test.find_all('a', attrs={'class': 'link_item'})[cate_num].getText())
        # only OKcashbag & Cashwork test...
        if "OK캐쉬백 오퀴즈" in category_name or "캐시워크 돈버는퀴즈" in category_name:
            print(category_name)
            category_href = bs_Test.find_all('a', attrs={'class': 'link_item'})[cate_num]["href"]
            save_path = './answer/{}/{}'.format(category_name, date_str)
            if not utils.check_exist(save_path):
                utils.make_folder(save_path)
            for page_num in range(1, 6):
                date_text = '{}월{}일'.format(today_date.month, today_date.day)
                blog_list_url = 'https://luckyquiz.tistory.com/{}?page={}'.format(
                    category_href, page_num)
                bs = BeautifulSoup(
                    urllib.request.urlopen(blog_list_url).read(), 'html.parser')
                for post in range(len(bs.select('.post-item'))):
                    post_title = bs.select('.post-item')[post].find('span', {'class': 'title'})
                    if not date_text in post_title.getText():
                        # print('Not today post.')
                        continue
                    blog_crawling_url = 'https://luckyquiz.tistory.com/{}'.format(
                        bs.select('.post-item')[post].find('a')['href'][1:5])
                    # print(bs.select('.post-item')[0].find('a')['href'][1:5])
                    day_crawling(blog_crawling_url, category_name, date_str, date_text)
        else:
            continue



if __name__ == '__main__':
    main()