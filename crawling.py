import urllib
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import utils
import requests
from datetime import date
import json

def day_crawling(url, date_text):
    test_url = url
    today_date = date.today()
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
    with open("./캐시워크/{}/{}.json".format(date.today(), title), 'w', encoding='UTF-8-sig') as outfile:
        json.dump(data, outfile, ensure_ascii=False, indent=4)
    print(title)
    print(questions)
    print(answer)

def main():
    save_path = './캐시워크/{}'.format(date.today())
    if not utils.check_exist(save_path):
        utils.make_folder(save_path)
    for page_num in range(1, 6):
        today_date = date.today()
        date_text = '{}월{}일'.format(today_date.month, today_date.day)
        blog_list_url = 'https://luckyquiz.tistory.com/category/%EC%BA%90%EC%8B%9C%EC%9B%8C%ED%81%AC%20%EB%8F%88%EB%B2%84%EB%8A%94%ED%80%B4%EC%A6%88?page={}'.format(
            page_num)
        bs = BeautifulSoup(
            urllib.request.urlopen(blog_list_url).read(), 'html.parser')
        for post in range(len(bs.select('.post-item'))):
            post_title = bs.select('.post-item')[post].find('span', {'class': 'title'})
            if not date_text in post_title.getText():
                print('Not today post.')
                break
            blog_crawling_url = 'https://luckyquiz.tistory.com/{}?category=748685'.format(
                bs.select('.post-item')[post].find('a')['href'][1:5])
            # print(bs.select('.post-item')[0].find('a')['href'][1:5])
            day_crawling(blog_crawling_url, date_text)

if __name__ == '__main__':
    main()