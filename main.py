import socket
import requests
import json
from bs4 import BeautifulSoup
import os
import app_config
import utils
import crawling_quiz
import crawling_fortune
import time
import random
import re
from datetime import date, datetime

origin = 'out'
output_type = 'json'  # 'xml' xml 기능 구현 안됨
# https://tistory.github.io/document-tistory-apis/  # api 설명서
# https://limsee.com/325 토큰 얻는 방법


def json_parsing(response_json):
    json_text = json.dumps(response_json, indent=4, ensure_ascii=False)
    return json_text


def write_json_file(file_name, json_text):
    with open(origin + '/' + file_name, "w", encoding='utf-8') as fp:
        fp.write(json_text)


def blog_info():
    '''
    GET https://www.tistory.com/apis/blog/info?
    access_token={access-token}
    &output={output-type}
    응답
    id: 사용자 로그인 아이디
    userId: 사용자 id
    blogs
        url: 티스토리 기본 url
        secondaryUrl: 독립도메인 url
        title: 블로그 타이틀
        description: 블로그 설명
        default: 대표블로그 여부 (Y/N)
        blogIconUrl: 블로그 아이콘 URL
        faviconUrl: 파비콘 URL
        profileThumbnailImageUrl: 대표이미지 썸네일 URL
        profileImageUrl: 대표이미지 URL
        blogId: 블로그 아이디
        nickname: 블로그에서의 닉네임
        role: 블로그 권한
        statistics: 블로그 컨텐츠 개수
        post: 글 수
        comment: 댓글 수
        trackback: 트랙백 수
        guestbook: 방명록 수
        invitation: 초대장 수
    '''
    url = 'https://www.tistory.com/apis/blog/info'
    data = {'access_token': app_config.access_token, 'output': output_type}
    res = requests.get(url, params=data)
    print(res.url)
    if res.status_code == 200:
        json_text = json_parsing(res.json())
        print(json_text)
        write_json_file('blog_info.json', json_text)

    else:
        json_text = json_parsing(res.json())
        print(json_text)


def blog_category_list(blog_name):
    '''
    GET https://www.tistory.com/apis/category/list?
    access_token={access-token}
    &output={output-type}
    &blogName={blog-name}
    blogName: Blog 이름
    '''
    url = 'https://www.tistory.com/apis/category/list'
    data = {'access_token': app_config.access_token, 'output': output_type, 'blogName': blog_name}
    res = requests.get(url, params=data)

    if res.status_code == 200:
        json_text = json_parsing(res.json())
        print(json_text)
        write_json_file('blog_category_list_' + blog_name + '.json', json_text)
    else:
        json_text = json_parsing(res.json())
        print(json_text)


def blog_list(blog_name, page):
    url = 'https://www.tistory.com/apis/post/list'
    '''
    GET https://www.tistory.com/apis/post/list?
        access_token={access-token}
        &output={output-type}
        &blogName={blog-name}
        &page={page-number}
    blogName: Blog 이름
    page: 불러올 페이지 번호입니다. 1부터 시작    
    '''
    data = {'access_token': app_config.access_token, 'output': output_type, 'blogName': blog_name, 'page': page}
    res = requests.get(url, params=data)
    print(res.url)
    if res.status_code == 200:
        json_text = json_parsing(res.json())
        print(json_text)
        write_json_file('blog_list_' + blog_name + '_' + str(page) + '.json', json_text)
    else:
        json_text = json_parsing(res.json())
        print(json_text)


def blog_read(blog_name, post_id):
    url = 'https://www.tistory.com/apis/post/read'
    '''
    blogName: Blog 이름
    postId: 글 ID - 리스트 얻기로 알 수 있음
    '''
    data = {'access_token': app_config.access_token, 'output': output_type, 'blogName': blog_name, 'postId': post_id}
    res = requests.get(url, params=data)
    print(res.url)
    if res.status_code == 200:
        json_text = json_parsing(res.json())
        print(json_text)
        write_json_file('blog_read_' + blog_name + '_' + str(post_id) + '.json', json_text)
    else:
        json_text = json_parsing(res.json())
        print(json_text)


def blog_write(blog_name, category_id, title, content, tag, today_date, now_time):
    url = 'https://www.tistory.com/apis/post/write'
    visibility = 3
    published = ''
    slogan = ''
    acceptComment = 1
    password = ''
    '''
    blogName: Blog Name (필수)
    title: 글 제목 (필수)
    content: 글 내용
    visibility: 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
    category: 카테고리 아이디 (기본값: 0)
    published: 발행시간 (TIMESTAMP 이며 미래의 시간을 넣을 경우 예약. 기본값: 현재시간)
    slogan: 문자 주소
    tag: 태그 (',' 로 구분)
    acceptComment: 댓글 허용 (0, 1 - 기본값)
    password: 보호글 비밀번호
    '''
    data = {'access_token': app_config.access_token, 'output': output_type, 'blogName': blog_name, 'title': title,
            'content': content, 'visibility': visibility, 'category': category_id, 'published': published,
            'slogan': slogan, 'tag': tag, 'acceptComment': acceptComment, 'password': password}
    res = requests.post(url, data=data)
    print(res.url)
    # today results path check
    if not utils.check_exist('./out/{}'.format(today_date)):
        utils.make_folder('./out/{}'.format(today_date))
    # Status
    if res.status_code == 200:
        time_dict = dict({"time": now_time})
        res = res.json()
        res.update(time_dict)
        json_text = json_parsing(res)
        print(json_text)
        write_name = 'blog_write_' + blog_name + '_' + category_id + '_' + title + '.json'
        write_json_file('{}/'.format(today_date) + write_name, json_text)
    else:
        json_text = json_parsing(res.json())
        print(json_text)


def blog_update(blog_name, category_id, title, content, tag, today_date, now_time, postId):
    url = 'https://www.tistory.com/apis/post/modify'
    visibility = 3
    published = ''
    slogan = ''
    acceptComment = 1
    password = ''
    '''
    blogName: Blog Name (필수)
    title: 글 제목 (필수)
    content: 글 내용
    visibility: 발행상태 (0: 비공개 - 기본값, 1: 보호, 3: 발행)
    category: 카테고리 아이디 (기본값: 0)
    published: 발행시간 (TIMESTAMP 이며 미래의 시간을 넣을 경우 예약. 기본값: 현재시간)
    slogan: 문자 주소
    tag: 태그 (',' 로 구분)
    acceptComment: 댓글 허용 (0, 1 - 기본값)
    password: 보호글 비밀번호
    '''
    data = {'access_token': app_config.access_token, 'output': output_type, 'blogName': blog_name, 'postId': postId,
            'title': title, 'content': content, 'visibility': visibility, 'category': category_id, 'published': published,
            'slogan': slogan, 'tag': tag, 'acceptComment': acceptComment, 'password': password}
    res = requests.post(url, data=data)
    print(res.url)
    # today results path check
    if not utils.check_exist('./out/{}'.format(today_date)):
        utils.make_folder('./out/{}'.format(today_date))
    # Status
    if res.status_code == 200:
        time_dict = dict({"time": now_time})
        res = res.json()
        res.update(time_dict)
        json_text = json_parsing(res)
        print(json_text)
        write_name = 'blog_write_' + blog_name + '_' + category_id + '_' + title + '.json'
        write_json_file('{}/'.format(today_date) + write_name, json_text)
    else:
        json_text = json_parsing(res.json())
        print(json_text)


def blog_upload(blog_name, uploadedfile_path, now_time):
    '''
        POST https://www.tistory.com/apis/post/attach?
        access_token={access-token}
        &blogName={blog-name}
        [uploadedfile]
        blogName: Blog Name 입니다.
        uploadedfile: 업로드할 파일 (multipart/form-data)
    '''
    files = {"uploadedfile": open(uploadedfile_path, 'rb')}
    url = 'https://www.tistory.com/apis/post/attach'
    data = {'access_token': app_config.access_token, 'blogName': blog_name}
    res = requests.post(url, params=data, files=files)
    print(res.url)
    if res.status_code == 200:
        print(res.text)
        time_dict = dict({"time": now_time})
        time_text = json_parsing(time_dict)
        # 업로드된 URL 주소
        soup = BeautifulSoup(res.text, 'lxml')
        url = soup.select_one('url')
        print(url.text)
        write_json_file('blog_upload_' + blog_name + '_' + os.path.split(uploadedfile_path)[1].split('.jpg')[0]+ '.txt', url.text)
        return url.text
    else:
        json_result, json_text = json_parsing(res.text)
        print(json_text)


def wrote_check(wrote_list, category_id, title, today_date, post_answer_text=' 빠른 정답 확인 여기로!'):
    pre_text = 'blog_write_tastediary_{}_'.format(category_id)
    json_ext = '.json'
    for wrote_name in wrote_list:
        if pre_text not in wrote_name:
            continue
        sp_wrote_name = wrote_name.split(pre_text)
        sp_wrote_name = sp_wrote_name[1].split(json_ext)[0]
        sp_wrote_name = sp_wrote_name.split(post_answer_text)[0]
        title = title.split(post_answer_text)[0]
        title_words_list = title.split(' ')
        wrote_name_words_list = sp_wrote_name.split(' ')
        real_title = []
        if len(title_words_list) != len(wrote_name_words_list):
            for t_words in title_words_list:
                match_word = re.findall(t_words, sp_wrote_name)
                if match_word:
                    real_title.append(match_word[0])
                else:
                    continue
            new_title = " ".join(real_title)
            if new_title == sp_wrote_name:
                wrote_json = utils.json_load('out/{}/{}{}{}'.format(today_date, pre_text, new_title + post_answer_text, json_ext))
                return True, new_title + post_answer_text, wrote_json['time'], wrote_json['tistory']['postId']
            elif new_title != sp_wrote_name:
                count = 0
                for w_words in wrote_name_words_list:
                    for t_words in title_words_list:
                        if w_words == t_words:
                            count += 1
                        else:
                            continue
                poe = count / len(title_words_list)
                if poe > 0.81:
                    wrote_json = utils.json_load(
                        'out/{}/{}{}{}'.format(today_date, pre_text, sp_wrote_name + post_answer_text, json_ext))
                    return True, sp_wrote_name + post_answer_text, wrote_json['time'], wrote_json['tistory']['postId']
                else:
                    False, False, None, None
            else:
                continue
        elif len(title_words_list) == len(wrote_name_words_list):
            count = 0
            for w_words in wrote_name_words_list:
                for t_words in title_words_list:
                    if w_words == t_words:
                        count += 1
                    else:
                        continue
            poe = count / len(title_words_list)
            if poe > 0.81:
                wrote_json = utils.json_load(
                    'out/{}/{}{}{}'.format(today_date, pre_text, sp_wrote_name + post_answer_text, json_ext))
                return True, sp_wrote_name + post_answer_text, wrote_json['time'], wrote_json['tistory']['postId']
            else:
                False, False, None, None
        elif title in sp_wrote_name:
            wrote_json = utils.json_load(
                'out/{}/{}{}{}'.format(today_date, pre_text, title + post_answer_text, json_ext))
            return True, False, wrote_json['time'], wrote_json['tistory']['postId']
        else:
            continue
    return False, False, None, None


def create_quiz_html(html_path, main_folder, quiz_folder, day_answer, img_name, category_id, today_date):
    h = open(html_path + '/' + main_folder + '.html', 'r+', encoding='UTF-8')
    f = open(os.path.join(quiz_folder, day_answer), encoding="UTF-8-sig")
    answer = json.loads(f.read())
    attach = utils.create_qa(answer)
    html = h.read()
    ads = utils.read_ads()
    other_answer = utils.check_other_answers(category_id, today_date)
    img_url = blog_upload('tastediary', './jpg/{}.jpg'.format(img_name), now_time)
    html = html.format(attach=attach, img=img_url, ads=ads, other_answer=other_answer)
    # print(html)
    h.close()
    f.close()
    return html


def create_fortune_html(main_folder, daily_path, day_fortune, today_date):
    h = open(main_folder + os.path.join('/', 'fortune.html'), 'r+', encoding='UTF-8')
    f = open(os.path.join(daily_path, day_fortune), encoding="UTF-8-sig")
    answer = json.loads(f.read())
    attach = utils.create_fortune(answer)
    zodiac = day_fortune.split('.json')[0]
    # "id": "1040594",
    # "name": "오늘의 운세",
    html = h.read()
    ads = utils.read_ads()
    now_time = datetime.now().strftime("%H:%M")
    img_url = blog_upload('tastediary', './jpg/fortune.jpg', now_time)
    html = html.format(attach=attach, img=img_url, ads=ads, today_date=today_date, zodiac=zodiac)
    # print(html)
    h.close()
    f.close()
    return html


if __name__ == '__main__':
    # Main Path
    fortune_5min_count = 0
    fortune_day_flag = 0 # '0' means not writing, '1' means wrote
    while(True):
        quiz_answer_path = './answer/'
        fortune_main_path = './fortune/'
        # date_str -> "%y-%m-%d" or date.today()
        # date_str = "2021-12-10"
        date_str = date.today()
        now_time_init = datetime.now().strftime("%H:%M")
        morning = '09:00'
        night = '21:00'
        morning_min = utils.hour_to_minutes(morning)
        night_min = utils.hour_to_minutes(night)
        now_min = utils.hour_to_minutes(now_time_init)
        if now_min >= night_min: # or now_min <= morning_min
            print(f'I am gonna go to bed... current_time : {now_time_init}')
            loop_forever = True
            while loop_forever:
                now_time_loop = datetime.now().strftime("%H:%M")
                now_min_sleeping = utils.hour_to_minutes(now_time_loop)
                print(f'Sleeping...zZ ---[current_time]--- : {now_time_loop}')
                time.sleep(60)
                if morning_min <= now_min_sleeping <= night_min:
                    loop_forever = False
                    print(f'I wake up! ---[current_time]--- : {now_time_loop}')
        if date_str.__class__.__name__ == 'date':
            today_date = date_str
        else:
            today_date = datetime.strptime(date_str, "%Y-%m-%d")
            today_date = today_date.date()
        # Create out folder
        if not utils.check_exist('out/{}'.format(today_date)):
            utils.make_folder('out/{}'.format(today_date))
        print(f'Crawling start.\n')
        # Crawling quiz
        crawling_quiz.main(today_date)
        if not utils.check_exist('fortune/{}'.format(date_str)):
            utils.make_folder('fortune/{}'.format(date_str))
        # Crawling daily's fortune
        if not len(utils.read_folder_list('./fortune/{}'.format(today_date))) == 12:
            crawling_fortune.main(today_date)
        answer_folder_list = utils.read_folder_list(quiz_answer_path)
        fortune_daily_path = fortune_main_path + os.path.join('/', datetime.strftime(today_date, "%Y-%m-%d"))
        fortune_daily_list = utils.read_folder_list(fortune_daily_path)
        write_check_list = utils.read_folder_list('out/{}'.format(today_date))
        if fortune_5min_count == 3:
            # Choice one from today's zodiac
            while True:
                day_fortune = random.choice(fortune_daily_list)
                today_str_title = '{}월{}일'.format(today_date.month, today_date.day)
                new_title = '{} {} 오늘의 운세를 알아보자!'.format(today_str_title, day_fortune.split('.json')[0])
                exists_check, title_check, wrote_time, postId = wrote_check(write_check_list, '1040594', new_title,
                                                                            today_date, ' 오늘의 운세를 알아보자!')
                if exists_check == True:
                    pass
                else:
                    new_html = create_fortune_html(fortune_main_path,
                                                   fortune_daily_path,
                                                   day_fortune,
                                                   today_date)
                    now_time = datetime.now().strftime("%H:%M")
                    blog_write('tastediary', '1040594', new_title, new_html, 'tag', today_date, now_time)
                    fortune_5min_count = 0
                    break
        for folder in answer_folder_list:
            # only '캐시워크' Testing ...
            if folder == '캐시워크 돈버는퀴즈':
                html_path = os.path.join(quiz_answer_path, folder)
                quiz_folder = os.path.join(os.path.join(quiz_answer_path, folder), datetime.strftime(today_date, "%Y-%m-%d"))
                answer_list = utils.read_sort_timelist(quiz_folder)
                now_time = datetime.now().strftime("%H:%M")
                for day_answer in answer_list:
                    write_check_list = utils.read_folder_list('out/{}'.format(today_date))
                    write_check_json = utils.json_load_utf8('answer/{}/{}/{}'.format(folder, today_date, day_answer))
                    if not write_check_json['post'][0]['question']:
                        continue
                    # new_title = day_answer.split('.json')[0] + ' 빠른 정답 확인 여기로!'
                    new_title = day_answer.split('.json')[0] + ' 8282 정답 여기서 보세요!'
                    new_title = new_title.replace("(", "").replace(")", "")
                    exists_check, title_check, wrote_time, postId = wrote_check(write_check_list, '1005221', new_title, today_date, ' 8282 정답 여기서 보세요!')
                    if not title_check is False:
                        new_title = title_check
                    if exists_check:
                        if utils.hour_to_minutes(now_time) - utils.hour_to_minutes(wrote_time) >= 5:
                            # update_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                            #                           'cashwork', '1037142', today_date)
                            update_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                                                      'cashwork', '1005221', today_date)
                            # blog_update('tastediary', '1037142', new_title, update_html, 'tag', today_date, now_time,
                            #             postId)
                            blog_update('all-snowball-effect', '1005221', new_title, update_html, 'tag', today_date, now_time,
                                        postId)
                            time.sleep(5)
                    else:
                        # new_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                        #                        'cashwork', '1037142', today_date)
                        new_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                                               'cashwork', '1005221', today_date)
                        # category id '1037142' - 배부른 소크라테스 - 돈버는 캐시워크
                        # blog_write('tastediary', '1037142', new_title, new_html, 'tag', today_date, now_time)
                        blog_write('all-snowball-effect', '1005221', new_title, new_html, 'tag', today_date, now_time)
                        time.sleep(5)
            # only 'OK캐쉬백 오퀴즈' Testing...
            if folder == 'OK캐쉬백 오퀴즈':
                html_path = os.path.join(quiz_answer_path, folder)
                quiz_folder = os.path.join(os.path.join(quiz_answer_path, folder), datetime.strftime(today_date, "%Y-%m-%d"))
                answer_list = utils.read_sort_timelist(quiz_folder)
                now_time = datetime.now().strftime("%H:%M")
                for day_answer in answer_list:
                    write_check_list = utils.read_folder_list('out/{}'.format(today_date))
                    write_check_json = utils.json_load_utf8('answer/{}/{}/{}'.format(folder, today_date, day_answer))
                    if not write_check_json['post'][0]['question']:
                        continue
                    # new_title = day_answer.split('.json')[0] + ' 빠른 정답 확인 여기로!'
                    new_title = day_answer.split('.json')[0] + ' 8282 정답 여기서 보세요!'
                    exists_check, title_check, wrote_time, postId = wrote_check(write_check_list, '1010176', new_title, today_date, ' 8282 정답 여기서 보세요!')
                    if not title_check is False:
                        new_title = title_check
                    if exists_check:
                        if utils.hour_to_minutes(now_time) - utils.hour_to_minutes(wrote_time) >= 5:
                            # update_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                            #                           'okcash', '1039667', today_date)
                            update_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                                                      'okcash', '1010176', today_date)
                            # blog_update('tastediary', '1039667', new_title, update_html, 'tag', today_date, now_time,
                            #             postId)
                            blog_update('all-snowball-effect', '1010176', new_title, update_html, 'tag', today_date, now_time,
                                        postId)
                            time.sleep(5)
                    else:
                        # new_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                        #                        'okcash', '1039667', today_date)
                        new_html = create_quiz_html(html_path, folder, quiz_folder, day_answer,
                                               'okcash', '1010176', today_date)
                        # category id '1039667' - 배부른 소크라테스 - OK캐쉬백 오퀴즈
                        # blog_write('tastediary', '1039667', new_title, new_html, 'tag', today_date, now_time)
                        blog_write('all-snowball-effect', '1010176', new_title, new_html, 'tag', today_date, now_time)
                        time.sleep(5)
            else:
                continue
        print(f'Work is done.')
        print(f'I am gonna take a break... current_time : {now_time}')
        fortune_5min_count += 1
        time.sleep(360)
        print(f'fortune time is {fortune_5min_count}')
        print(f'Working time! current_time : {now_time}')

    # utils.check_folder(origin)
    # 계정 블로그 정보들 읽기
    # blog_info()

    # 블로그 리스트 읽기
    # blog_list('tastediary', 1)

    # 블로그 카테고리 읽기
    # blog_category_list('tastediary')

    # 게시물 작성
    # blog_write('tastediary', '0', '캐시워크 테스트', html, 'tag')

    # 게시물 읽기
    # blog_read('chandong83', 200)

    # 파일 첨부
    # blog_upload('chandong83', 'oroca.png')