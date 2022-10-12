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
import ssl

MAX_RETRY = 5


def get_html(html_url, timeout=30, decode='utf-8'):
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


def get_category(title):
    blog_list_url = 'https://luckyquiz3.blogspot.com/'
    blog_list_read = get_html(blog_list_url)
    bs_Test = BeautifulSoup(blog_list_read, 'html.parser')
    category_len = len(bs_Test.find_all('a', attrs={'role': 'menuitem'}))
    for cate_num in range(category_len):
        category_name = utils.remove_slash_ntr(bs_Test.find_all('a', attrs={'role': 'menuitem'})[cate_num].getText())
        if category_name == '우리원멤버스 데일리퀴즈':
            category_name = '우리원(WON)멤버스 데일리퀴즈'
        category_name_list = category_name.split(' ')
        for c_name in category_name_list:
            if c_name in title:
                return category_name


def day_crawling_blogspot(url, category_name):
    socket.setdefaulttimeout(20)
    headers = {'User-Agent': 'Quiz_bot'}
    test_url = url
    time.sleep(5)
    req = requests.get(test_url, headers=headers)
    if req.status_code == 404:
        pass
    res_read = get_html(test_url)
    bs = BeautifulSoup(res_read, 'html.parser')
    title = bs.find('title').get_text()
    answer = []
    questions = []
    attach = ''
    # results = bs.select('div.post-body.post-content')[0].contents
    results = bs.find("div", {'id': "quizarea"})
    for i in results:
        # print(i.get_text())
        if '\n' in i:
            continue
        elif '<script>' in i.get_text():
            continue
        else:
            str_i = str(i)
            if '토실행운퀴즈' in str_i:
                str_i = str_i.replace("토실행운퀴즈", "buy-the-dip")
            answer.append(str_i)
    for j in answer:
        attach += j
    html_r = open('./answer/{}/{}.html'.format(category_name, category_name))
    html = html_r.read()
    html = html.format(attach=attach)
    html_r.close()
    utils.save_html(title, './html', html)
    # bs.select('div.post-body.post-content')[0].get_text().split('[퀴즈]')[1]
    return True


def day_crawling_tistory(url, category_name, today_date, date_text):
    socket.setdefaulttimeout(20)
    headers = {'User-Agent': 'Quiz_bot'}
    test_url = url
    time.sleep(5)
    req = requests.get(test_url, headers=headers)
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
        if '정답은' in i.get_text() and '입니다.' in i.get_text():
            if '블로그 이용방법 숙지하기(클릭)' in i.get_text():
                continue
            else:
                questions.append(results[results_count - 1].get_text(strip=True))
                answer.append(results[results_count].get_text(strip=True))
                results_count += 1
        else:
            results_count += 1
            continue
    questions = utils.remove_xa0(questions)
    questions = utils.remove_quo_marks(questions)
    questions = utils.remove_bracket(questions)
    answer = utils.remove_xa0(answer)
    title = utils.remove_slash_ntr(title)
    data = {}
    data['post'] = []
    data['count'] = [len(questions)]
    for n in range(len(questions)):
        data['post'].append({"question": questions[n], "answer": answer[n]})
    with open("./answer/{}/{}/{}.json".format(category_name, today_date, title), 'w', encoding='UTF-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    print(title)
    print(questions)
    print(answer)


def main(today_date):
    # excluded name
    ex_name = []
    # date_str -> "%y-%m-%d" or date.today()
    # date_str = date.today()
    date_str = today_date
    if date_str.__class__.__name__ == 'date':
        today_date = date_str
    else:
        today_date = datetime.strptime(date_str, "%Y-%m-%d")
    ### New version - blogspot ###
    blog_list_url = 'https://luckyquiz3.blogspot.com/search/label/%EC%BA%90%EC%8B%9C%EC%9B%8C%ED%81%AC%20%EB%8F%88%EB%B2%84%EB%8A%94%ED%80%B4%EC%A6%88?&max-results=15' # 캐시워크 돈버는 퀴즈
    blog_list_read = get_html(blog_list_url)
    bs_Test = BeautifulSoup(blog_list_read, 'html.parser')
    today_publish_check = '{}월{}일'.format(int(today_date.month), int(today_date.day))
    for i in range(1, len(bs_Test.find_all('a', attrs={'class': 'entry-excerpt excerpt'}))):
        title = bs_Test.find_all('a', attrs={'class': 'entry-title-link'})[i]['title']
        if today_publish_check in title:
            print(title)
            category_name = get_category(title)
            url = bs_Test.find_all('a', attrs={'class': 'entry-excerpt excerpt'})[i]['href']
            print(category_name)
            save_path = './answer/{}/{}'.format(category_name, date_str)
            if not utils.check_exist(save_path):
                utils.make_folder(save_path)
            blog_crawling_url = url
            day_crawling_blogspot(blog_crawling_url, category_name)

    print('done')
    ### old version - tistory ###
    '''
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
            for page_num in range(1, 4):
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
    '''


if __name__ == '__main__':
    main('2022-09-08')
