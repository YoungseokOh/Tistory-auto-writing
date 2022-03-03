import os
import errno
import json
import random
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from mplfinance.original_flavor import candlestick2_ohlc


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
    temp_str = temp_str.replace("/", "")
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
    answer_close = "</p><p></p>"
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
        attach = attach + answer_close
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


def shuffle_title(title):
    temp_shuffle_title = title.split(' ')
    random.shuffle(temp_shuffle_title)
    temp_shuffle_title = list(filter(None, temp_shuffle_title))
    title = ' '.join(temp_shuffle_title)
    return title


def search(data_path, extension):
    """Returns the list of files have extension (only current directory)
    Args:
        data_path (str): data path
        extension (str): extension
    Returns:
        file_list (list): file list with path
   """
    file_list = []
    for filename in os.listdir(data_path):
        ext = os.path.splitext(filename)[-1]
        if ext == extension:
            file_list.append(data_path+'/'+filename)
    return file_list


def strdate_convert(date):
    return datetime.strptime(date, "%Y-%m-%d")


def get_today_ymd():
    return datetime.today().strftime("%Y-%m-%d")


def plot_technical_indicators(name, dataset, last_days):
    plt.rc('font', family='NanumGothic')
    dataset = dataset.iloc[-last_days:, :]

    # dataset = dataset.reset_index()
    dataset = dataset.set_index(dataset['date'])
    ax = plt.subplot2grid((6,4), (0,0), rowspan=4, colspan=4)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
    #ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    #ax.spines['bottom'].set_color("#5998ff")
    #ax.spines['top'].set_color("#5998ff")
    #ax.spines['left'].set_color("#5998ff")
    #ax.spines['right'].set_color("#5998ff")
    ax.yaxis.label.set_color("k")
    ax.tick_params(axis='y', colors='k')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax.tick_params(axis='x', colors='w')
    x_ = list(dataset.index)
    x_range = []
    col_name = []
    for col_list in dataset.columns:
        if "ema" in col_list:
            col_name.append(col_list)
    for i in range(0, int(len(x_))):
        x_range.append(dataset['date'].iloc[i])
        #print(x_range)
    # Plot first subplot
    candlestick2_ohlc(ax, dataset['open'], dataset['high'], dataset['low'], dataset['close'], width=0.5, colorup='r', colordown='b')
    ax.plot(dataset['{}'.format(col_name[0])], label='{}'.format(col_name[0].upper()), color='g', linestyle='-.', linewidth=0.8)
    ax.plot(dataset['{}'.format(col_name[1])], label='{}'.format(col_name[1].upper()), color='r', linestyle='-.', linewidth=0.8)
    ax.plot(dataset['{}'.format(col_name[2])], label='{}'.format(col_name[2].upper()), color='b', linestyle='-.', linewidth=0.8)
    if 'upper_band' in dataset.columns:
        # ax.plot(dataset['upper_band'], label='Upper Band', color='gray', linewidth=0.25)
        # ax.plot(dataset['lower_band'], label='Lower Band', color='gray', linewidth=0.25)
        ax.fill_between(x_, dataset['lower_band'], dataset['upper_band'], alpha=0.15, color='yellow', label='Bollinger Band')
    plt.title('Technical indicators for {} - last {} days.'.format(name, last_days))
    ax.set_ylabel('KRW')
    ax.legend()
    #axv.ylabel('Volume')
    # plt.xticks(x_[::30], x_range[::30])
    # xlabels = ax.get_xticklabels()
    # ax.set_xticklabels(xlabels, rotation=45, fontsize=7)

    axv = plt.subplot2grid((6, 4), (4, 0), sharex=ax, rowspan=1, colspan=4)

    axv.xaxis.set_major_locator(mticker.MaxNLocator(10))
    #axv.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    #axv.plot(dataset['volume'], color='c', linewidth=0.5)
    axv.bar(range(len(dataset['volume'])), dataset['volume'], color='m', linewidth=0.5)

    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    #axv.spines['bottom'].set_color("#5998ff")
    #axv.spines['top'].set_color("#5998ff")
    #axv.spines['left'].set_color("#5998ff")
    #axv.spines['right'].set_color("#5998ff")
    axv.tick_params(axis='x', colors='w')
    axv.tick_params(axis='y', colors='k')

    axv.set_ylabel('volume')
    axv.yaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='upper'))

    axv1 = plt.subplot2grid((6, 4), (5, 0), sharex=ax, rowspan=1, colspan=4)
    axv1.xaxis.set_major_locator(mticker.MaxNLocator(5))
    #axv1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axv1.plot(dataset['rsi'], color='black', linewidth=0.5)
    axv1.set_yticks([30, 50, 70])
    axv1.set_ylabel('rsi')


    '''
    for label in axv.xaxis.get_ticklabels():
        label.set_rotation(45)
    plt.setp(ax.get_xticklabels(), visible=False)
    '''
    #plt.setp(axv.get_xticklabels(), visible=False)
    #axv = ax.twinx()
    #print(dataset['volume'])
    #
    plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
    # plt.legend()
    plt.grid(True)
    # plt.show() # Figure test
    fig_save = plt.gcf()
    return fig_save