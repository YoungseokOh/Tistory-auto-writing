import urllib
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import utils
import requests
from datetime import date, datetime
import json


def day_crawling(url, category_name, today_date, date_text):
    test_url = url
    req = requests.get(test_url)
    if req.status_code == 404:
        pass
    bs = BeautifulSoup(
        urllib.request.urlopen(test_url).read(), 'html.parser')
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
            questions.append(results[results_count-1].get_text(strip=True))
            answer.append(results[results_count].get_text(strip=True))
            results_count += 1
        else:
            results_count += 1
            continue
    questions = utils.remove_xa0(questions)
    data = {}
    data['post'] = []
    data['count'] = [len(questions)]
    for n in range(len(questions)):
        data['post'].append({"question": questions[n], "answer":answer[n]})
    with open("./{}/{}/{}.json".format(category_name, today_date, title), 'w', encoding='UTF-8-sig') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    print(title)
    print(questions)
    print(answer)


def main():
    # For test
    date_str = '2021-11-19'
    today_date = datetime.strptime(date_str, "%Y-%m-%d")
    blog_list_url = 'https://luckyquiz.tistory.com/category/'
    bs_Test = BeautifulSoup(
        urllib.request.urlopen(blog_list_url).read(), 'html.parser')
    category_len = len(bs_Test.find_all('a', attrs={'class': 'link_item'}))
    for cate_num in range(category_len):
        category_name = utils.remove_slash_nt(bs_Test.find_all('a', attrs={'class': 'link_item'})[cate_num].getText())
        print(category_name)
        category_href = bs_Test.find_all('a', attrs={'class': 'link_item'})[cate_num]["href"]
        save_path = './{}/{}'.format(category_name, date_str)
        if not utils.check_exist(save_path):
            utils.make_folder(save_path)
        for page_num in range(1, 6):
            #today_date = date.today()
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


if __name__ == '__main__':
    main()