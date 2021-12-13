import os
import errno
import json


def check_folder(folder):
    try:
        if not(os.path.isdir(folder)):
            os.makedirs(os.path.join(folder))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print(folder + ' is not created.')
            raise
        return False
    return True


def readlines(filename):
    """Read all the lines in a text file and return as a list
    """
    with open(filename, 'r') as f:
        lines = f.read().splitlines()
    return lines


def read_folder_list(path):
    folder_list = os.listdir(path)
    return folder_list


def read_sort_timelist(path):
    filelist = [s for s in os.listdir(path)
                if os.path.isfile(os.path.join(path, s))]
    filelist.sort(key=lambda s: os.path.getmtime(os.path.join(path, s)), reverse=True)
    return filelist


def check_exist(path):
    return os.path.exists(path)


def make_folder(path):
    return os.makedirs(path)


def check_folder(path):
    if not check_exist(path):
        make_folder(path)
    return True


def remove_xa0(list):
    temp_list = []
    for i in list:
        temp = i.replace(u'\xa0', u' ')
        temp_list.append(temp)
    return temp_list


def remove_quo_marks(list):
    temp_list = []
    for i in list:
        temp = i.replace('"', '')
        temp_list.append(temp)
    return temp_list


def remove_bracket(list):
    temp_list = []
    for i in list:
        temp = i.replace("(", "").replace(")", "")
        temp_list.append(temp)
    return temp_list


def remove_slash_ntr(str):
    temp_str = str.replace("\n", "")
    temp_str = temp_str.replace("\r", "")
    str = temp_str.replace("\t", "")
    str = str.split("(")[0]
    return str


def real_answer(str):
    str_temp = str.split('정답은')
    str_temp = str_temp[1]
    str = str_temp.split('입니다.')
    str = str[0]
    return str


def create_fortune(day_fortune):
    attach = ""
    p_open = "<p style="'"text-align: center; font-size: 15pt; color : #00B050; font-weight: bold;"'" data-ke-size="'"size15"'">{year}년생"
    p_close = "</p>"
    zodiac_open = "<p style="'"text-align: center; font-size: 16pt;"'" data-ke-size="'"size16"'"><b>{content}</b>"
    zodiac_close = "</p>"
    k_count = 0
    for k in day_fortune.keys():
        attach = attach + p_open.format(year=k)
        attach = attach + p_close
        attach = attach + zodiac_open.format(content=day_fortune['{}'.format(k)])
        attach = attach + zodiac_close
        k_count += 1
    return attach


def create_qa(answer):
    attach = ""
    p_open = "<p style="'"text-align: center; font-size: 12pt;"'" data-ke-size="'"size12"'">"
    p_close = "</p>"
    answer_open = "<p style="'"text-align: center; font-size: 18pt;"'" data-ke-size="'"size18"'"><b>정답은<span style="'"color: #115CB4;"'">" \
                  "<span>&nbsp;{ans}</span><span>&nbsp;</span></span>입니다.</b></p>"
    answer_close = "</p>"
    for n in range(int(answer['count'][0])):
        attach = attach + p_open
        question = answer['post'][n]['question']
        attach = attach + question
        attach = attach + p_open
        attach = attach + p_close
        ans = answer['post'][n]['answer']
        ans = real_answer(ans)
        ans = answer_open.format(ans=ans)
        attach = attach + ans
        attach = attach + p_close
        print(attach)
    return attach


def json_load(path):
    json_text = open(path).read()
    dict_json = json.loads(json_text)
    return dict_json


def json_load_utf8(path):
    with open(path, "r", encoding="utf-8") as fp:
        dict_json = json.load(fp)
    return dict_json


def hour_to_minutes(str):
    str = str.split(':')
    hour = int(str[0])
    minutes = int(str[1])
    total_min = hour * 60 + minutes
    return total_min


def find_original_title(str, pre, post, ext):
    pre_text = pre
    post_answer_text = post
    json_ext = ext
    str = str.split(pre_text)
    str = str[1].split(json_ext)[0]
    str = str.split(post_answer_text)[0]
    return str


def read_ads():
    ### Inplay ads
    # ads = '<script async src='"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2895485609612928"'' \
    #       'crossorigin='"anonymous"'></script>' \
    #       '<ins class='"adsbygoogle"'style='"display:block; text-align:center;"'data-ad-layout='"in-article"'data-ad-format='"fluid"'data-ad-client='"ca-pub-2895485609612928"'data-ad-slot='"1085028600"'></ins>' \
    #       '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'

    ### Display ads
    ads = '<script async src='"https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-2895485609612928"' crossorigin="anonymous"></script>' \
          '<!-- Cashwork 디스플레이 본문 -->' \
          '<ins class="adsbygoogle" ' \
          'style="display:block"' \
          'data-ad-client="ca-pub-2895485609612928"' \
          'data-ad-slot="3057473877"' \
          'data-ad-format="auto"' \
          'data-full-width-responsive="true"></ins>' \
          '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>'
    return ads


def check_other_answers(category_id, today_date):
    other_answer = ""
    json_ext = '.json'
    oa_format = '<p data-ke-size='"size25"' align='"center"' style='"font-size: 25pt; font-family: 'Nanum Gothic';"'><a href='"{}"' target = '"_blank"' rel = '"noopener"'>{}</a></p>'
    space = '<p data-ke-size='"size11"'>&nbsp;</p>'
    pre_text = 'blog_write_tastediary_{}_'.format(category_id)
    other_answer_list = read_folder_list('out/{}'.format(today_date))
    if not other_answer_list:
        return other_answer
    for o_answer in other_answer_list:
        if pre_text in o_answer:
            sp_wrote_name = o_answer.split(pre_text)
            sp_wrote_name = sp_wrote_name[1].split(json_ext)[0]
            o_answer_json = json_load('out/{}/{}'.format(today_date, o_answer))
            other_answer_url = o_answer_json['tistory']['url']
            other_answer = other_answer + oa_format.format(other_answer_url, sp_wrote_name)
            other_answer = other_answer + space
    return other_answer


# Duplicate from main(quiz)
def json_parsing(response_json):
    json_text = json.dumps(response_json, indent=4, ensure_ascii=False)
    return json_text

